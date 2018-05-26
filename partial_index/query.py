"""Django Q object to SQL string conversion."""
from django.db.models.sql import Query


class Vendor(object):
    POSTGRESQL = 'postgresql'
    SQLITE = 'sqlite'


def get_valid_vendor(schema_editor):
    vendor = schema_editor.connection.vendor
    if vendor not in [Vendor.POSTGRESQL, Vendor.SQLITE]:
        raise ValueError('Database vendor %s is not supported by django-partial-index.' % vendor)
    return vendor


def q_to_sql(q, model, schema_editor):
    # Q -> SQL conversion based on code from Ian Foote's Check Constraints pull request:
    # https://github.com/django/django/pull/7615/

    query = Query(model)
    where = query._add_q(q, used_aliases=set(), allow_joins=False)[0]
    connection = schema_editor.connection
    compiler = connection.ops.compiler('SQLCompiler')(query, connection, 'default')
    sql, params = where.as_sql(compiler, connection)
    params = tuple(map(schema_editor.quote_value, params))
    where_sql = sql % params
    return where_sql
