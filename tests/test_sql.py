"""
Tests for SQL CREATE INDEX statements.
"""
from django.db import connection
from django.test import TestCase
import re

from partial_index import PartialIndex
from testapp.models import RoomBooking, Job


ROOMBOOKING_SQL = r'^CREATE UNIQUE INDEX "testapp_[a-zA-Z0-9_]+_partial" ON "testapp_roombooking" \("user_id", "room_id"\) WHERE deleted_at IS NULL;?$'
JOB_NONUNIQUE_SQL = r'^CREATE INDEX "testapp_[a-zA-Z0-9_]+_partial" ON "testapp_job" \("order" DESC\) WHERE is_complete = %s;?$'
JOB_UNIQUE_SQL = r'^CREATE UNIQUE INDEX "testapp_[a-zA-Z0-9_]+_partial" ON "testapp_job" \("group"\) WHERE is_complete = %s;?$'


class PartialIndexSqlTest(TestCase):
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

    def test_roombooking_createsql(self):
        with self.schema_editor() as editor:
            sql = RoomBooking._meta.indexes[0].create_sql(RoomBooking, editor)
        self.assertRegex(sql, ROOMBOOKING_SQL)

    def test_roombooking_create_model(self):
        with self.schema_editor() as editor:
            editor.create_model(RoomBooking)
        self.assertContainsMatch(editor.collected_sql, ROOMBOOKING_SQL)

    def test_job_createsql(self):
        with self.schema_editor() as editor:
            sql = Job._meta.indexes[0].create_sql(Job, editor)
            self.assertRegex(sql, JOB_NONUNIQUE_SQL % self.false(editor))

    def test_job_create_model(self):
        with self.schema_editor() as editor:
            editor.create_model(Job)
            f = self.false(editor)
        self.assertContainsMatch(editor.collected_sql, JOB_NONUNIQUE_SQL % f)
        self.assertContainsMatch(editor.collected_sql, JOB_UNIQUE_SQL % f)


class PartialIndexCreateTest(TestCase):
    """Check that the index really can be added to and removed from the model in the DB."""

    def schema_editor(self):
        # Actually execute statements.
        return connection.schema_editor()

    @staticmethod
    def get_constraints(model):
        """Get the indexes on the table using a new cursor."""
        with connection.cursor() as cursor:
            return connection.introspection.get_constraints(cursor, model._meta.db_table)

    def test_unique(self):
        num_constraints_before = len(self.get_constraints(RoomBooking))

        # Add the index
        index_name = 'roombooking_test_idx'
        index = PartialIndex(fields=['user', 'room'], name=index_name, unique=True, where='deleted_at IS NULL')
        with self.schema_editor() as editor:
            editor.add_index(RoomBooking, index)
        constraints = self.get_constraints(RoomBooking)
        self.assertEqual(len(constraints), num_constraints_before + 1)
        self.assertEqual(constraints[index_name]['columns'], ['user_id', 'room_id'])
        self.assertEqual(constraints[index_name]['primary_key'], False)
        self.assertEqual(constraints[index_name]['check'], False)
        self.assertEqual(constraints[index_name]['index'], True)
        self.assertEqual(constraints[index_name]['unique'], True)

        # Drop the index
        with self.schema_editor() as editor:
            editor.remove_index(RoomBooking, index)
        constraints = self.get_constraints(RoomBooking)
        self.assertEqual(len(constraints), num_constraints_before)
        self.assertNotIn(index_name, constraints)

    def test_not_unique(self):
        num_constraints_before = len(self.get_constraints(Job))

        # Add the index
        index_name = 'job_test_idx'
        index = PartialIndex(fields=['-group'], name=index_name, unique=False, where_postgresql='is_complete = false', where_sqlite='is_complete = 0')
        with self.schema_editor() as editor:
            editor.add_index(Job, index)
        constraints = self.get_constraints(Job)
        self.assertEqual(len(constraints), num_constraints_before + 1)
        self.assertEqual(constraints[index_name]['columns'], ['group'])
        self.assertEqual(constraints[index_name]['orders'], ['DESC'])
        self.assertEqual(constraints[index_name]['primary_key'], False)
        self.assertEqual(constraints[index_name]['check'], False)
        self.assertEqual(constraints[index_name]['index'], True)
        self.assertEqual(constraints[index_name]['unique'], False)

        # Drop the index
        with self.schema_editor() as editor:
            editor.remove_index(Job, index)
        constraints = self.get_constraints(Job)
        self.assertEqual(len(constraints), num_constraints_before)
        self.assertNotIn(index_name, constraints)
