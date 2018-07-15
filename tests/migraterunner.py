#!/usr/bin/env python
import argparse
import subprocess

from django.core import management
import os
from os.path import abspath, dirname, exists, join
import sys

try:
    from io import StringIO
except ImportError:
    from cStringIO import StringIO

REPO_DIR = dirname(dirname(abspath(__file__)))
TESTS_DIR = join(REPO_DIR, 'tests')
SQLITE_PATH = join(REPO_DIR, 'test_migrations_partial_index.sqlite3')
POSTGRESQL_TABLE = 'test_migrations_partial_index'

sys.path.append(REPO_DIR)
sys.path.append(TESTS_DIR)


DATABASES_FOR_DB = {
    'postgresql': {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': POSTGRESQL_TABLE,
        }
    },
    'sqlite': {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': SQLITE_PATH,
        }
    },
}


def create_database(args):
    if args.db == 'postgresql':
        # subprocess.check_call(['dropdb', '--if-exists', POSTGRESQL_TABLE])
        subprocess.check_call(['createdb', '--encoding', 'utf-8', POSTGRESQL_TABLE])
    else:
        pass


def destroy_database(args):
    if args.db == 'postgresql':
        subprocess.check_call(['dropdb', '--if-exists', POSTGRESQL_TABLE])
    else:
        if exists(SQLITE_PATH):
            os.remove(SQLITE_PATH)


def main(args):
    try:
        create_database(args)

        # Since this test suite is designed to be ran outside of ./manage.py test, we need to do some setup first.
        import django
        from django.conf import settings
        settings.configure(INSTALLED_APPS=['testmigrationsapp'], DATABASES=DATABASES_FOR_DB[args.db])
        django.setup()

        management.call_command('migrate', 'testmigrationsapp', verbosity=1)

        import django.db
        django.db.connections.close_all()
    finally:
        destroy_database(args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', required=True)
    args = parser.parse_args()
    main(args)
