# Provide a nicer error message than failing to import models.Index.

VERSION = (0, 3, 0)
__version__ = '.'.join(str(v) for v in VERSION)


MIN_DJANGO_VERSION = (1, 11)
DJANGO_VERSION_ERROR = 'Django version %s or later is required for django-partial-index.' % '.'.join(str(v) for v in MIN_DJANGO_VERSION)

try:
    import django
except ImportError:
    raise ImportError(DJANGO_VERSION_ERROR)

if tuple(django.VERSION[:2]) < MIN_DJANGO_VERSION:
    raise ImportError(DJANGO_VERSION_ERROR)


from django.db.models import Index


class PartialIndex(Index):
    suffix = 'partial'
    # Allow an index name longer than 30 characters since this index can only be used on PostgreSQL and SQLite,
    # and the Django default 30 character limit for cross-database compatibility isn't applicable.
    # The "partial" suffix is 4 letters longer than the default "idx".
    max_name_length = 34
    sql_create_index = {
        'postgresql': 'CREATE%(unique)s INDEX %(name)s ON %(table)s%(using)s (%(columns)s)%(extra)s WHERE %(where)s',
        'sqlite': 'CREATE%(unique)s INDEX %(name)s ON %(table)s%(using)s (%(columns)s) WHERE %(where)s',
    }

    # Mutable default fields=[] looks wrong, but it's copied from super class.
    def __init__(self, fields=[], name=None, unique=None, where='', where_postgresql='', where_sqlite=''):
        if unique not in [True, False]:
            raise ValueError('Unique must be True or False')
        if where:
            if where_postgresql or where_sqlite:
                raise ValueError('If providing a single where predicate, must not provide where_postgresql or where_sqlite')
        else:
            if not where_postgresql and not where_sqlite:
                raise ValueError('At least one where predicate must be provided')
            if where_postgresql == where_sqlite:
                raise ValueError('If providing a separate where_postgresql and where_sqlite, then they must be different.' +
                                 'If the same expression works for both, just use single where.')
        self.unique = unique
        self.where = where
        self.where_postgresql = where_postgresql
        self.where_sqlite = where_sqlite
        super(PartialIndex, self).__init__(fields, name)

    def __repr__(self):
        if self.where:
            anywhere = "where='%s'" % self.where
        else:
            anywhere = "where_postgresql='%s', where_sqlite='%s'" % (self.where_postgresql, self.where_sqlite)

        return "<%(name)s: fields=%(fields)s, unique=%(unique)s, %(anywhere)s>" % {
            'name': self.__class__.__name__,
            'fields': "'{}'".format(', '.join(self.fields)),
            'unique': self.unique,
            'anywhere': anywhere
        }

    def deconstruct(self):
        path, args, kwargs = super(PartialIndex, self).deconstruct()
        kwargs['unique'] = self.unique
        kwargs['where'] = self.where
        kwargs['where_postgresql'] = self.where_postgresql
        kwargs['where_sqlite'] = self.where_sqlite
        return path, args, kwargs

    def get_valid_vendor(self, schema_editor):
        vendor = schema_editor.connection.vendor
        if vendor not in self.sql_create_index:
            raise ValueError('Database vendor %s is not supported for django-partial-index.' % vendor)
        return vendor

    def get_sql_create_template_values(self, model, schema_editor, using):
        parameters = super(PartialIndex, self).get_sql_create_template_values(model, schema_editor, using)
        parameters['unique'] = ' UNIQUE' if self.unique else ''
        # Note: the WHERE predicate is not yet checked for syntax or field names, and is inserted into the CREATE INDEX query unescaped.
        # This is bad for usability, but is not a security risk, as the string cannot come from user input.
        vendor = self.get_valid_vendor(schema_editor)
        if vendor == 'postgresql':
            parameters['where'] = self.where_postgresql or self.where
        elif vendor == 'sqlite':
            parameters['where'] = self.where_sqlite or self.where
        else:
            raise ValueError('Should never happen')
        return parameters

    def create_sql(self, model, schema_editor, using=''):
        vendor = self.get_valid_vendor(schema_editor)
        # Only change from super function - override query template to insert optional UNIQUE at start, and WHERE at the end.
        sql_template = self.sql_create_index[vendor]
        sql_parameters = self.get_sql_create_template_values(model, schema_editor, using)
        return sql_template % sql_parameters

    def name_hash_extra_data(self):
        return [str(self.unique), self.where, self.where_postgresql, self.where_sqlite]

    def set_name_with_model(self, model):
        """Sets an unique generated name for the index.

        PartialIndex would like to only override "hash_data = ...", but the entire method must be duplicated for that.
        """
        table_name = model._meta.db_table
        column_names = [model._meta.get_field(field_name).column for field_name, order in self.fields_orders]
        column_names_with_order = [
            (('-%s' if order else '%s') % column_name)
            for column_name, (field_name, order) in zip(column_names, self.fields_orders)
        ]
        # The length of the parts of the name is based on the default max
        # length of 30 characters.
        hash_data = [table_name] + column_names_with_order + [self.suffix] + self.name_hash_extra_data()
        self.name = '%s_%s_%s' % (
            table_name[:11],
            column_names[0][:7],
            '%s_%s' % (self._hash_generator(*hash_data), self.suffix),
        )
        assert len(self.name) <= self.max_name_length, (
            'Index too long for multiple database support. Is self.suffix '
            'longer than 3 characters?'
        )
        self.check_name()
