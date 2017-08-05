import django.db.backends.postgresql.schema
from django.db.models import Index


class PartialIndex(Index):
    suffix = 'partial'
    # Allow an index name longer than 30 characters since this index can only be used on PostgreSQL and SQLite,
    # and the Django default 30 character limit for cross-database compatibility isn't applicable.
    # PostgreSQL limit is 63 and SQLite does not have a limit.
    max_name_length = 60
    sql_create_index = "CREATE%(unique)s INDEX %(name)s ON %(table)s%(using)s (%(columns)s)%(extra)s WHERE %(where)s"

    def __init__(self, fields=[], name=None, unique=None, where=''):
        if unique not in [True, False]:
            raise ValueError('unique must be True or False.')
        if not where:
            raise ValueError('where predicate must be provided.')
        self.unique = unique
        self.where = where
        super(PartialIndex, self).__init__(fields, name)

    def __repr__(self):
        return '<%(name)s: fields=%(fields)s, unique=%(unique)s, where="%(where)s">' % {
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
        if not isinstance(schema_editor, django.db.backends.postgresql.schema.DatabaseSchemaEditor):
            raise ValueError('PartialIndex so far only supports the PostgreSQL backend. SQLite could be added, MySQL and Oracle do not support them at all.')
        # Only change from super function - override query template to insert optional UNIQUE at start, and WHERE at the end.
        sql_create_index = self.sql_create_index
        sql_parameters = self.get_sql_create_template_values(model, schema_editor, using)
        return sql_create_index % sql_parameters
