"""
Tests for SQL CREATE INDEX statements.
"""

from django.db import connection
from django.db.models import Q, F
from django.test import TestCase

from partial_index import query
from testapp.models import AB, ABC


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


class QueryMentionedFieldsTest(TestCase):
    def assertMentioned(self, q, fields):
        self.assertEqual(set(query.q_mentioned_fields(q, ABC)), set(fields))

    def test_empty(self):
        self.assertMentioned(Q(), [])

    def test_single_const(self):
        self.assertMentioned(Q(a=123), ['a'])

    def test_single_const_exact(self):
        self.assertMentioned(Q(a__exact=123), ['a'])

    def test_single_null(self):
        self.assertMentioned(Q(a__isnull=True), ['a'])
        self.assertMentioned(Q(a__isnull=False), ['a'])

    def test_two_const(self):
        self.assertMentioned(Q(a=12, b=34), ['a', 'b'])

    def test_two_null(self):
        self.assertMentioned(Q(a=12, b__isnull=True), ['a', 'b'])

    def test_f_equal(self):
        self.assertMentioned(Q(a=F('b')), ['a', 'b'])

    def test_f_add(self):
        self.assertMentioned(Q(a=F('b') + F('c') + 1), ['a', 'b', 'c'])

    def test_contains_f(self):
        self.assertMentioned(Q(a__contains='Hello', b=F('c')), ['a', 'b', 'c'])

    def test_or(self):
        self.assertMentioned(Q(a=12) | Q(b=34), ['a', 'b'])

    def test_or_duplicate(self):
        self.assertMentioned(Q(a=12, b=34) | Q(b=56), ['a', 'b'])

    def test_or_extra(self):
        self.assertMentioned(Q(a=12, b=34) | Q(c=56), ['a', 'b', 'c'])
