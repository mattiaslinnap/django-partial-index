# Provide a nicer error message than failing to import models.Index.

VERSION = (0, 2, 0)
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
    def __init__(self, fields=[], name=None, unique=None, where=''):
        if unique not in [True, False]:
            raise ValueError('unique must be True or False')
        if not where:
            raise ValueError('where predicate must be provided')
        self.unique = unique
        self.where = where
        super(PartialIndex, self).__init__(fields, name)

    def __repr__(self):
        return "<%(name)s: fields=%(fields)s, unique=%(unique)s, where='%(where)s'>" % {
            'name': self.__class__.__name__,
            'fields': "'{}'".format(', '.join(self.fields)),
            'unique': self.unique,
            'where': self.where,
        }

    def deconstruct(self):
        path, args, kwargs = super(PartialIndex, self).deconstruct()
        kwargs['unique'] = self.unique
        kwargs['where'] = self.where
        return path, args, kwargs

    def get_sql_create_template_values(self, model, schema_editor, using):
        parameters = super(PartialIndex, self).get_sql_create_template_values(model, schema_editor, using)
        parameters['unique'] = ' UNIQUE' if self.unique else ''
        # Note: the WHERE predicate is not yet checked for syntax or field names, and is inserted into the CREATE INDEX query unescaped.
        # This is bad for usability, but is not a security risk, as the string cannot come from user input.
        parameters['where'] = self.where
        return parameters

    def create_sql(self, model, schema_editor, using=''):
        vendor = schema_editor.connection.vendor
        if vendor not in self.sql_create_index:
            raise ValueError('Database vendor %s is not supported for django-partial-index.' % vendor)

        # Only change from super function - override query template to insert optional UNIQUE at start, and WHERE at the end.
        sql_template = self.sql_create_index[vendor]
        sql_parameters = self.get_sql_create_template_values(model, schema_editor, using)
        return sql_template % sql_parameters
