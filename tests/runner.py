#!/usr/bin/env python
import argparse
from os.path import abspath, dirname, join
import sys

REPO_DIR = dirname(dirname(abspath(__file__)))
TESTS_DIR = join(REPO_DIR, 'tests')

sys.path.append(REPO_DIR)
sys.path.append(TESTS_DIR)


DATABASES_FOR_DB = {
    'postgresql': {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'partial_index',
        }
    },
    'sqlite': {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': join(REPO_DIR, 'db.sqlite3'),
        }
    },
}


def main(args):
    # Since this test suite is designed to be ran outside of ./manage.py test, we need to do some setup first.
    import django
    from django.conf import settings
    settings.configure(INSTALLED_APPS=['testapp'], DATABASES=DATABASES_FOR_DB[args.db])
    django.setup()

    from django.test.runner import DiscoverRunner
    test_runner = DiscoverRunner(top_level=TESTS_DIR, interactive=False, keepdb=False)
    if args.testpaths:
        paths = ['tests.' + p for p in args.testpaths]
        failures = test_runner.run_tests(paths)
    else:
        failures = test_runner.run_tests(['tests'])
    if failures:
        sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', required=True)
    parser.add_argument('testpaths', nargs='*')
    args = parser.parse_args()
    main(args)
