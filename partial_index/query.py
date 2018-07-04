"""Django Q object to SQL string conversion."""

from django.db.models import expressions
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


def expression_mentioned_fields(exp):
    if isinstance(exp, expressions.Col):
        field = exp.output_field or exp.field  # TODO: which one makes sense to use here?
        if field and field.name:
            return [field.name]
    elif hasattr(exp, 'get_source_expressions'):
        child_fields = []
        for source in exp.get_source_expressions():
            child_fields.extend(expression_mentioned_fields(source))
        return child_fields
    else:
        raise NotImplementedError('Unexpected expression class %s=%s when looking up mentioned fields.' % (exp.__class__.__name__, exp))


def q_mentioned_fields(q, model):
    """Returns list of field names mentioned in Q object.

    Q(a__isnull=True, b=F('c')) -> ['a', 'b', 'c']
    """
    query = Query(model)
    where = query._add_q(q, used_aliases=set(), allow_joins=False)[0]
    return list(sorted(set(expression_mentioned_fields(where))))
