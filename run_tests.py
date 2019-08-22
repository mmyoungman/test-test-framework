# Created by Mark Youngman on 05 August 2019

from os import path, makedirs, remove, walk
import argparse
import importlib
import cProfile
import pstats
from tests.TestSuite import TestSuite

parser = argparse.ArgumentParser(prog="python run_tests.py",
                                 description="Runs test suites founds in the tests/ "
                                 "directory")
parser.add_argument("--file",
                    dest="file",
                    default="tests/",
                    metavar="{file/dir}",
                    help="run a particular test suite or test suites within a directory")
parser.add_argument("--sync",
                    dest="sync",
                    action="store_true",
                    help="run test suites synchronously")
parser.add_argument("--include",
                    dest="inc_tags",
                    default='',
                    metavar="{tag(s)}",
                    help="specify tags of tests you wish to exclusively run, separated by commas")
parser.add_argument("--exclude",
                    dest="exc_tags",
                    default='',
                    metavar="{tag(s)}",
                    help="specify tags of tests you wish to not run, separated by commas")
parser.add_argument("--profile",
                    dest="profile",
                    action="store_true",
                    help="output profiling information")
parser.add_argument("--quiet",
                    dest="quiet",
                    action="store_true",
                    help="don't print to console")
args = parser.parse_args()

args.inc_tags = [tag for tag in args.inc_tags.split(',') if tag != '']
args.exc_tags = [tag for tag in args.exc_tags.split(',') if tag != '']

if not path.exists('test-results/'):
    makedirs('test-results/')

def filepath_to_import_str(filepath):
    assert filepath.endswith('.py')
    filepath = filepath[:-3]
    import_str = filepath.replace(path.sep, '.')
    return import_str

assert path.exists(args.file)
if path.isfile(args.file):
    assert args.file.endswith('.py')
    assert args.file not in ['__init__.py', 'TestSuite.py']
    importlib.import_module(filepath_to_import_str(args.file))
elif path.isdir(args.file):
    from glob import glob
    files = [y for x in walk(args.file) for y in glob(path.join(x[0], '*.py'))]
    for filepath in files:
        importlib.import_module(filepath_to_import_str(filepath))

if args.profile:
    results = {}
    for test_suite in TestSuite.__subclasses__():
        cProfile.run('test_suite(args.quiet).run_tests(results, \
                                                       inc_tags=args.inc_tags, \
                                                       exc_tags=args.exc_tags)',
                     'profile-data')
        stream = open('test-results/python-profiling-' + test_suite.__name__ + '.log', 'w')
        p = pstats.Stats('profile-data', stream=stream)
        p.sort_stats('cumulative')
        p.print_stats()
        remove('profile-data')
        stream.close()
elif args.sync or len(TestSuite.__subclasses__()) == 1:
    results = {}
    for test_suite in TestSuite.__subclasses__():
        test_suite(args.quiet).run_tests(results,
                                         inc_tags=args.inc_tags,
                                         exc_tags=args.exc_tags)
else:
    import multiprocessing as mp
    pool = mp.Pool()
    results = mp.Manager().dict()
    jobs = []

    for test_suite in TestSuite.__subclasses__():
        res = pool.apply_async(test_suite(args.quiet).run_tests,
                               args=(results,),
                               kwds={'inc_tags': args.inc_tags,
                                     'exc_tags': args.exc_tags})
        jobs.append(res)

    for job in jobs:
        job.wait()

print('\nREPORT TIME\n')
for suite_name, suite_dict in results.items():
    print('Suite: ' + suite_name +
          ' Overall result: ' + suite_dict['result'].name +
          ' Overall time: ' + suite_dict['time'])
    for test in suite_dict['tests']:
        print('Name: ' + test[0] +
              ' Result: ' + test[1].name +
              ' Time: ' + test[2])
    print()
