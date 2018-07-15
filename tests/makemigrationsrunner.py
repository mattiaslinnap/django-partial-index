#!/usr/bin/env python
import argparse
from django.core import management
from os.path import abspath, dirname, exists, join
import sys


REPO_DIR = dirname(dirname(abspath(__file__)))
TESTS_DIR = join(REPO_DIR, 'tests')


sys.path.append(REPO_DIR)
sys.path.append(TESTS_DIR)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}


def main(args):
    # Since this test suite is designed to be ran outside of ./manage.py test, we need to do some setup first.
    import django
    from django.conf import settings
    settings.configure(INSTALLED_APPS=['testmigrationsapp'], DATABASES=DATABASES)
    django.setup()
    management.call_command('makemigrations', 'testmigrationsapp', verbosity=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    main(args)
