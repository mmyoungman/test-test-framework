# Created by Mark Youngman on 05 August 2019

from os import path, makedirs, remove, walk
from glob import glob
import argparse
import importlib
import cProfile
import pstats
import multiprocessing as mp
from tests.TestSuite import TestSuite, Result

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


def file_path_to_import_str(file_path):
    assert file_path.endswith('.py')
    file_path = file_path[:-3]
    import_str = file_path.replace(path.sep, '.')
    return import_str


assert path.exists(args.file)
if path.isfile(args.file):
    assert args.file.endswith('.py')
    assert args.file not in ['__init__.py', 'TestSuite.py']
    importlib.import_module(file_path_to_import_str(args.file))
else:  # isdir
    files = [y for x in walk(args.file) for y in glob(path.join(x[0], '*.py'))]
    for file_path in files:
        importlib.import_module(file_path_to_import_str(file_path))

assert len(TestSuite.__subclasses__()) > 0, 'There should be a test suite to run!'


def run_suite(suite, args, results):
    if args.profile:
        cProfile.runctx('suite(args.quiet).run_tests(results, \
                                                     inc_tags=args.inc_tags, \
                                                     exc_tags=args.exc_tags)',
                        globals(),
                        locals(),
                        f'profile-data-{suite.__name__}')
        stream = open(f'test-results/python-profiling-{suite.__name__}.log', 'w')
        p = pstats.Stats(f'profile-data-{suite.__name__}', stream=stream)
        p.sort_stats('cumulative')
        p.print_stats()
        remove(f'profile-data-{suite.__name__}')
        stream.close()
    else:
        suite(args.quiet).run_tests(results,
                                    inc_tags=args.inc_tags,
                                    exc_tags=args.exc_tags)


if args.sync or len(TestSuite.__subclasses__()) == 1:
    results = {}
    for test_suite in TestSuite.__subclasses__():
        run_suite(test_suite, args, results)
else:
    pool = mp.Pool()
    results = mp.Manager().dict()
    jobs = []
    for test_suite in TestSuite.__subclasses__():
        job = pool.apply_async(run_suite,
                               args=(test_suite, args, results))
        jobs.append(job)
    for job in jobs:
        job.wait()

print('\nREPORT TIME\n')
assert isinstance(results, dict) or isinstance(results, mp.managers.DictProxy)
assert results, "results shouldn't be empty"

# Print to result to console
for suite_name, suite_dict in results.items():
    print('Suite: ' + suite_name +
          ' Overall result: ' + suite_dict['result'].name +
          ' Overall time: ' + suite_dict['time'])
    for test in suite_dict['tests']:
        print('Name: ' + test[0] +
              ' Result: ' + test[1].name +
              ' Time: ' + test[2])
    print()

# Produce xunit.xml
text = """<?xml version="1.0" encoding="UTF-8"?>
"""
for suite_name, suite_dict in results.items():
    text += f"""<testsuite classname="{suite_name}" tests="{suite_dict['count'][0]}" 
                           errors="{suite_dict['count'][4]}" failures="{suite_dict['count'][2]}" 
                           skipped="0" time="{suite_dict['time']}">\n"""
    for test in suite_dict['tests']:
        text += f"""<testcase classname="{suite_name} - {test[0]}" name="{test[0]}" time="{test[2]}">\n"""
        if test[1] in [Result.FAILED, Result.TEST_ERROR]:
            text += """<failure message="test failed" type="AssertionError"></failure>\n"""
        text += "</testcase>\n"
    text += "</testsuite>\n"

text_file = open("test-results/xunit.xml", "w")
text_file.write(text)
text_file.close()

