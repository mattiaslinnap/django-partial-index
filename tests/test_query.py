"""
Tests for SQL CREATE INDEX statements.
"""
from django.db import connection
from django.db.models import Q, F
from django.test import TestCase

from partial_index import query
from testapp.models import AB


class QueryToSqlTest(TestCase):
    """Check that Q object to SQL transformation is valid."""

    def schema_editor(self):
        # collect_sql=True -> do not actually execute.
        return connection.schema_editor(collect_sql=True)

    def assertQSql(self, q, expect_sql):
        with self.schema_editor() as editor:
            sql = query.q_to_sql(q, AB, editor)
        self.assertEqual(expect_sql, sql)

    def test_isnull(self):
        self.assertQSql(Q(a__isnull=True), '"testapp_ab"."a" IS NULL')

    def test_not_null(self):
        self.assertQSql(Q(a__isnull=False), '"testapp_ab"."a" IS NOT NULL')

    def test_a_equals_const(self):
        self.assertQSql(Q(a='Hello'), '"testapp_ab"."a" = \'Hello\'')

    def test_a_equals_const_exact(self):
        self.assertQSql(Q(a__exact='Hello'), '"testapp_ab"."a" = \'Hello\'')

    def test_a_equals_b(self):
        self.assertQSql(Q(a=F('b')), '"testapp_ab"."a" = ("testapp_ab"."b")')
