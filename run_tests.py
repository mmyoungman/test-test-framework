# Created by Mark Youngman on 05 August 2019

from os import listdir
import argparse
import importlib
from tests.TestSuite import TestSuite

parser = argparse.ArgumentParser(prog="python run_tests.py",
                                 description="Runs test suites founds in the tests/ "
                                 "directory")
parser.add_argument("--suite",
                    dest="suite",
                    help="run a particular suite only")
parser.add_argument("--sync",
                    dest="sync",
                    action="store_true",
                    help="run test suites synchronously")
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

args.inc_tags = [tag for tag in args.inc_tags.split(',') if tag != '']
args.exc_tags = [tag for tag in args.exc_tags.split(',') if tag != '']

# Import test suites
for filename in listdir('tests'):
    if filename.endswith('.py') and filename not in ['__init__.py', 'TestSuite.py']:
        importlib.import_module('tests.' + filename[:-3])

if args.suite:
    assert args.suite in [suite.__name__ for suite in TestSuite.__subclasses__()]
    for test_suite in TestSuite.__subclasses__():
        if test_suite.__name__ == args.suite:
            results = {}
            test_suite().run_tests(results,
                                   inc_tags=args.inc_tags,
                                   exc_tags=args.exc_tags)
elif args.sync:
    results = {}
    for test_suite in TestSuite.__subclasses__():
        test_suite().run_tests(results,
                               inc_tags=args.inc_tags,
                               exc_tags=args.exc_tags)
else:
    import multiprocessing as mp
    pool = mp.Pool()
    results = mp.Manager().dict()
    workers = []
    for test_suite in TestSuite.__subclasses__():
        res = pool.apply_async(test_suite().run_tests,
                               args=(results,),
                               kwds={'inc_tags': args.inc_tags,
                                     'exc_tags': args.exc_tags})
        workers.append(res)

    for worker in workers:
        worker.wait()

print(results)
