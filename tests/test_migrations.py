"""
Tests for actual use of the indexes after creating models with them.
"""
import subprocess
import re

from django.conf import settings
from django.test import TestCase
import os
from os.path import abspath, dirname, exists, join


TESTS = dirname(abspath(__file__))
IGNORE = ['__init__.py', '__pycache__', '.gitignore']
MIGS = join(TESTS, 'testmigrationsapp', 'migrations')


def listmigs():
    return list(sorted(fname for fname in os.listdir(MIGS) if fname not in IGNORE and not fname.endswith('.pyc')))


class MigrationsTestCase(TestCase):

    def delete_migrations_files(self):
        for fname in listmigs():
            os.remove(join(MIGS, fname))

    def makemigrations(self):
        return subprocess.check_output([join(TESTS, 'makemigrationsrunner.py')])

    def migrate(self):
        return subprocess.check_output([join(TESTS, 'migraterunner.py'), '--db', settings.DB_NAME])

    def test_makemigrations_first_file_made(self):
        self.delete_migrations_files()
        self.assertEqual(listmigs(), [])
        self.makemigrations()
        self.assertEqual(listmigs(), ['0001_initial.py'])
        self.delete_migrations_files()

    def test_makemigrations_contents(self):
        self.delete_migrations_files()
        self.assertEqual(listmigs(), [])
        self.makemigrations()
        content = open(join(MIGS, '0001_initial.py')).read()
        content = re.sub(r'\s', '', content)
        self.assertEqual(len(re.findall(r"migrations\.AddIndex\(model_name='[a-z]+',index=partial_index\.PartialIndex\(fields=\[", content)), 4)
        self.assertEqual(len(re.findall(r"where=partial_index\.PQ\(", content)), 4)
        self.assertEqual(len(re.findall(r"where_postgresql", content)), 0)
        self.assertEqual(len(re.findall(r"where_sqlite", content)), 0)
        self.delete_migrations_files()

    def test_makemigrations_second_time_file_not_changed(self):
        self.delete_migrations_files()
        self.assertEqual(listmigs(), [])
        self.makemigrations()
        self.assertEqual(listmigs(), ['0001_initial.py'])
        before = open(join(MIGS, '0001_initial.py')).read()
        self.makemigrations()
        self.assertEqual(listmigs(), ['0001_initial.py'])
        after = open(join(MIGS, '0001_initial.py')).read()
        self.assertEqual(before, after)
        self.delete_migrations_files()

    def test_migrate_succeeds(self):
        self.delete_migrations_files()
        self.makemigrations()
        migrateoutput = self.migrate()
        self.assertIn(b'Applying testmigrationsapp.0001_initial... OK', migrateoutput)
