"""
Tests for SQL CREATE INDEX statements.
"""
from django.db import connection
from django.test import TransactionTestCase
import re

from partial_index import PartialIndex, PQ
from testapp.models import RoomBookingText, JobText, ComparisonText, RoomBookingQ, JobQ, ComparisonQ


ROOMBOOKING_TEXT_SQL = r'^CREATE UNIQUE INDEX "testapp_[a-zA-Z0-9_]+_partial" ' + \
                       r'ON "testapp_roombookingtext" \("user_id", "room_id"\) ' + \
                       r'WHERE deleted_at IS NULL;?$'
ROOMBOOKING_Q_SQL =    r'^CREATE UNIQUE INDEX "testapp_[a-zA-Z0-9_]+_partial" ' + \
                       r'ON "testapp_roombookingq" \("user_id", "room_id"\) ' + \
                       r'WHERE "testapp_roombookingq"."deleted_at" IS NULL;?$'

JOB_TEXT_NONUNIQUE_SQL = r'^CREATE INDEX "testapp_[a-zA-Z0-9_]+_partial" ' + \
                         r'ON "testapp_jobtext" \("order" DESC\) ' + \
                         r'WHERE is_complete = %s;?$'
JOB_Q_NONUNIQUE_SQL =    r'^CREATE INDEX "testapp_[a-zA-Z0-9_]+_partial" ' + \
                         r'ON "testapp_jobq" \("order" DESC\) ' + \
                         r'WHERE "testapp_jobq"."is_complete" = %s;?$'

JOB_TEXT_UNIQUE_SQL = r'^CREATE UNIQUE INDEX "testapp_[a-zA-Z0-9_]+_partial" ' + \
                      r'ON "testapp_jobtext" \("group"\) ' + \
                      r'WHERE is_complete = %s;?$'
JOB_Q_UNIQUE_SQL =    r'^CREATE UNIQUE INDEX "testapp_[a-zA-Z0-9_]+_partial" ' + \
                      r'ON "testapp_jobq" \("group"\) ' + \
                      r'WHERE "testapp_jobq"."is_complete" = %s;?$'

COMPARISON_TEXT_SQL = r'^CREATE UNIQUE INDEX "testapp_[a-zA-Z0-9_]+_partial" ' + \
                      r'ON "testapp_comparisontext" \("a", "b"\) ' + \
                      r'WHERE a = b;?$'
COMPARISON_Q_SQL =    r'^CREATE UNIQUE INDEX "testapp_[a-zA-Z0-9_]+_partial" ' + \
                      r'ON "testapp_comparisonq" \("a", "b"\) ' + \
                      r'WHERE "testapp_comparisonq"."a" = \("testapp_comparisonq"."b"\);?$'


class PartialIndexSqlTest(TransactionTestCase):
    """Check that the schema editor generates valid SQL for the index."""

    def schema_editor(self):
        # collect_sql=True -> do not actually execute.
        return connection.schema_editor(collect_sql=True)

    def assertContainsMatch(self, texts, pattern):
        found = False
        for text in texts:
            if re.match(pattern, text):
                found = True
                break
        self.assertTrue(found, 'Pattern matching \"%s\" not found in %s' % (pattern, texts))

    def false(self, editor):
        return 'false' if editor.connection.vendor == 'postgresql' else '0'

    def test_roombooking_text_createsql(self):
        with self.schema_editor() as editor:
            sql = RoomBookingText._meta.indexes[0].create_sql(RoomBookingText, editor)
        self.assertRegex(sql, ROOMBOOKING_TEXT_SQL)

    def test_roombooking_q_createsql(self):
        with self.schema_editor() as editor:
            sql = RoomBookingQ._meta.indexes[0].create_sql(RoomBookingQ, editor)
        self.assertRegex(sql, ROOMBOOKING_Q_SQL)

    def test_roombooking_text_create_model(self):
        with self.schema_editor() as editor:
            editor.create_model(RoomBookingText)
        self.assertContainsMatch(editor.collected_sql, ROOMBOOKING_TEXT_SQL)

    def test_roombooking_q_create_model(self):
        with self.schema_editor() as editor:
            editor.create_model(RoomBookingQ)
        self.assertContainsMatch(editor.collected_sql, ROOMBOOKING_Q_SQL)

    def test_job_text_createsql(self):
        with self.schema_editor() as editor:
            sql = JobText._meta.indexes[0].create_sql(JobText, editor)
            self.assertRegex(sql, JOB_TEXT_NONUNIQUE_SQL % self.false(editor))

    def test_job_q_createsql(self):
        with self.schema_editor() as editor:
            sql = JobQ._meta.indexes[0].create_sql(JobQ, editor)
            self.assertRegex(sql, JOB_Q_NONUNIQUE_SQL % self.false(editor))

    def test_job_text_create_model(self):
        with self.schema_editor() as editor:
            editor.create_model(JobText)
            f = self.false(editor)
        self.assertContainsMatch(editor.collected_sql, JOB_TEXT_NONUNIQUE_SQL % f)
        self.assertContainsMatch(editor.collected_sql, JOB_TEXT_UNIQUE_SQL % f)

    def test_job_q_create_model(self):
        with self.schema_editor() as editor:
            editor.create_model(JobQ)
            f = self.false(editor)
        self.assertContainsMatch(editor.collected_sql, JOB_Q_NONUNIQUE_SQL % f)
        self.assertContainsMatch(editor.collected_sql, JOB_Q_UNIQUE_SQL % f)

    def test_comparison_text_createsql(self):
        with self.schema_editor() as editor:
            sql = ComparisonText._meta.indexes[0].create_sql(ComparisonText, editor)
        self.assertRegex(sql, COMPARISON_TEXT_SQL)

    def test_comparison_q_createsql(self):
        with self.schema_editor() as editor:
            sql = ComparisonQ._meta.indexes[0].create_sql(ComparisonQ, editor)
        self.assertRegex(sql, COMPARISON_Q_SQL)

    def test_comparison_text_create_model(self):
        with self.schema_editor() as editor:
            editor.create_model(ComparisonText)
        self.assertContainsMatch(editor.collected_sql, COMPARISON_TEXT_SQL)

    def test_comparison_q_create_model(self):
        with self.schema_editor() as editor:
            editor.create_model(ComparisonQ)
        self.assertContainsMatch(editor.collected_sql, COMPARISON_Q_SQL)


class PartialIndexCreateTest(TransactionTestCase):
    """Check that the index really can be added to and removed from the model in the DB."""

    def schema_editor(self):
        # Actually execute statements.
        return connection.schema_editor()

    @staticmethod
    def get_constraints(model):
        """Get the indexes on the table using a new cursor."""
        with connection.cursor() as cursor:
            return connection.introspection.get_constraints(cursor, model._meta.db_table)

    def assertAddRemoveConstraint(self, model, index_name, index, expect_attrs):
        num_constraints_before = len(self.get_constraints(model))

        # Add the index
        with self.schema_editor() as editor:
            editor.add_index(model, index)
        constraints = self.get_constraints(model)
        self.assertEqual(len(constraints), num_constraints_before + 1)
        for k, v in expect_attrs.items():
            self.assertEqual(constraints[index_name][k], v)

        # Drop the index
        with self.schema_editor() as editor:
            editor.remove_index(model, index)
        constraints = self.get_constraints(model)
        self.assertEqual(len(constraints), num_constraints_before)
        self.assertNotIn(index_name, constraints)

    def test_unique_text(self):
        index_name = 'roombookingtext_test_idx'
        index = PartialIndex(fields=['user', 'room'], name=index_name, unique=True, where='deleted_at IS NULL')
        self.assertAddRemoveConstraint(RoomBookingText, index_name, index, {
            'columns': ['user_id', 'room_id'],
            'primary_key': False,
            'check': False,
            'index': True,
            'unique': True,
        })

    def test_not_unique_text(self):
        index_name = 'jobtext_test_idx'
        index = PartialIndex(fields=['-group'], name=index_name, unique=False, where_postgresql='is_complete = false', where_sqlite='is_complete = 0')
        self.assertAddRemoveConstraint(JobText, index_name, index, {
            'columns': ['group'],
            'orders': ['DESC'],
            'primary_key': False,
            'check': False,
            'index': True,
            'unique': False,
        })

    def test_unique_q(self):
        index_name = 'roombookingq_test_idx'
        index = PartialIndex(fields=['user', 'room'], name=index_name, unique=True, where=PQ(deleted_at__isnull=True))
        self.assertAddRemoveConstraint(RoomBookingQ, index_name, index, {
            'columns': ['user_id', 'room_id'],
            'primary_key': False,
            'check': False,
            'index': True,
            'unique': True,
        })

    def test_not_unique_q(self):
        index_name = 'jobq_test_idx'
        index = PartialIndex(fields=['-group'], name=index_name, unique=False, where=PQ(is_complete=False))
        self.assertAddRemoveConstraint(JobQ, index_name, index, {
            'columns': ['group'],
            'orders': ['DESC'],
            'primary_key': False,
            'check': False,
            'index': True,
            'unique': False,
        })
