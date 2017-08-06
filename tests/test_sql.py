"""
Tests for SQL CREATE INDEX statements.
"""
from django.db import connection
from django.test import TestCase
import re


from testapp.models import RoomBooking, Job


ROOMBOOKING_SQL = r'^CREATE UNIQUE INDEX "testapp_[a-zA-Z0-9_]+_partial" ON "testapp_roombooking" \("user_id", "room_id"\) WHERE deleted_at IS NULL;?$'
JOB_SQL = r'^CREATE INDEX "testapp_[a-zA-Z0-9_]+_partial" ON "testapp_job" \("created_at" DESC\) WHERE is_complete = 0;?$'


class PartialIndexSqlTest(TestCase):
    def setUp(self):
        if connection.vendor == 'postgresql':
            from django.db.backends.postgresql.schema import DatabaseSchemaEditor as PgSchemaEditor
            self.schema = PgSchemaEditor(connection, collect_sql=True)
        elif connection.vendor == 'sqlite':
            from django.db.backends.sqlite3.schema import DatabaseSchemaEditor as LiteSchemaEditor
            self.schema = LiteSchemaEditor(connection, collect_sql=True)
        else:
            raise AssertionError('django-partial-index does not work with database vendor %s' % connection.vendor)

    def assertContainsMatch(self, texts, pattern):
        found = False
        for text in texts:
            if re.match(pattern, text):
                found = True
                break
        self.assertTrue(found, 'Pattern matching \"%s\" not found in %s' % (pattern, texts))

    def test_roombooking_createsql(self):
        sql = RoomBooking._meta.indexes[0].create_sql(RoomBooking, self.schema)
        self.assertRegex(sql, ROOMBOOKING_SQL)

    def test_roombooking_create_model(self):
        with self.schema:
            self.schema.create_model(RoomBooking)
        self.assertContainsMatch(self.schema.collected_sql, ROOMBOOKING_SQL)

    def test_job_createsql(self):
        sql = Job._meta.indexes[0].create_sql(Job, self.schema)
        self.assertRegex(sql, JOB_SQL)

    def test_job_create_model(self):
        with self.schema:
            self.schema.create_model(Job)
        self.assertContainsMatch(self.schema.collected_sql, JOB_SQL)
