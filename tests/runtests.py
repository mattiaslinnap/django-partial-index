#!/usr/bin/env python
from __future__ import print_function

import argparse
from os.path import abspath, dirname, join
import subprocess
import sys


REPO_DIR = dirname(dirname(abspath(__file__)))
TESTS_DIR = join(REPO_DIR, 'tests')
RUNNER_PY = join(TESTS_DIR, 'runner.py')


def main(args):
    exitcodes = []
    if not args.skip_postgresql:
        print('Testing with PostgreSQL...', file=sys.stderr)
        exitcodes.append(subprocess.call([RUNNER_PY, '--db', 'postgresql'] + args.testpaths))
        print('Done testing with PostgreSQL.', file=sys.stderr)
    print('', file=sys.stderr)
    if not args.skip_sqlite:
        print('Testing with SQLite...', file=sys.stderr)
        exitcodes.append(subprocess.call([RUNNER_PY, '--db', 'sqlite'] + args.testpaths))
        print('Done testing with SQLite.', file=sys.stderr)
    # Exit with 0 if all non-skipped tests did the same.
    sys.exit(max(exitcodes) or 0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs tests.')
    parser.add_argument('--skip-postgresql', default=False, action='store_true')
    parser.add_argument('--skip-sqlite', default=False, action='store_true')
    parser.add_argument('testpaths', nargs='*')
    args = parser.parse_args()
    main(args)
