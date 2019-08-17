# Created by Mark Youngman on 05 August 2019

from os import listdir
import argparse
from tests.TestSuite import TestSuite
import importlib

parser = argparse.ArgumentParser(prog="python run_tests.py",
                                 description="Runs test suites founds in the tests/ "
                                 "directory")
parser.add_argument("--suite",
                    dest="suite",
                    help="run a particular suite only")
parser.add_argument("--include",
                    dest="inc_tags",
                    nargs="?",
                    default='',
                    metavar="{tag(s)}",
                    help="specify tags of tests you wish to exclusively run, separated by commas")
parser.add_argument("--exclude",
                    dest="exc_tags",
                    nargs="?",
                    default='',
                    metavar="{tag(s)}",
                    help="specify tags of tests you wish to not run, separated by commas")
args = parser.parse_args()

args.inc_tags = [tag for tag in args.inc_tags.split(',')]
args.exc_tags = [tag for tag in args.exc_tags.split(',')]

# Import test suites
for filename in listdir('tests'):
    if filename.endswith('.py') and filename not in ['__init__.py', 'TestSuite.py']:
        filename = filename[:-3]
        importlib.import_module('tests.' + filename)

print("Subclasses: ", TestSuite.__subclasses__())

if args.suite:
    if args.suite not in [suite.__name__ for suite in TestSuite.__subclasses__()]:
        print("Invalid --suite argument specified")
    for test_suite in TestSuite.__subclasses__():
        if test_suite.__name__ == args.suite:
            results = {}
            test_suite().run_tests(results, inc_tags=args.inc_tags, exc_tags=args.exc_tags)
else:
    import multiprocessing as mp
    pool = mp.Pool()
    results = mp.Manager().dict()
    workers = []
    for test_suite in TestSuite.__subclasses__():
        res = pool.apply_async(test_suite().run_tests, args=(results,))
        workers.append(res)

    for worker in workers:
        worker.wait()

print(results)
