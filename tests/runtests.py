#!/usr/bin/env python

from os.path import abspath, dirname, join
import subprocess
import sys


REPO_DIR = dirname(dirname(abspath(__file__)))
TESTS_DIR = join(REPO_DIR, 'tests')
RUNNER_PY = join(TESTS_DIR, 'runner.py')


def main():
    print('Testing with PostgreSQL...', file=sys.stderr)
    ret1 = subprocess.call([RUNNER_PY, '--db_engine', 'django.db.backends.postgresql'])
    print('Done testing with PostgreSQL.', file=sys.stderr)
    print('', file=sys.stderr)
    print('Testing with SQLite...', file=sys.stderr)
    ret2 = subprocess.call([RUNNER_PY, '--db_engine', 'django.db.backends.sqlite3'])
    print('Done testing with SQLite.', file=sys.stderr)
    sys.exit(ret1 or ret2)


if __name__ == '__main__':
    main()
