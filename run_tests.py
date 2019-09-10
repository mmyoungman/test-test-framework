# Created by Mark Youngman on 05 August 2019

import os
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

if not os.path.exists('test-results/'):
    os.makedirs('test-results/')

# Import test suites
def file_path_to_import_str(file_path):
    assert file_path.endswith('.py')
    file_path = file_path[:-3]
    import_str = file_path.replace(os.path.sep, '.')
    return import_str


assert os.path.exists(args.file)
if os.path.isfile(args.file):
    assert args.file.endswith('.py')
    assert args.file not in ['__init__.py', 'TestSuite.py']
    importlib.import_module(file_path_to_import_str(args.file))
else:  # isdir
    files = [root + file_name for root, _, files in os.walk(args.file)
             for file_name in files if file_name.endswith('.py')]
    for file_path in files:
        importlib.import_module(file_path_to_import_str(file_path))

assert len(TestSuite.__subclasses__()) > 0, 'There should be a test suite to run!'

# Run test suites
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
        os.remove(f'profile-data-{suite.__name__}')
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

assert isinstance(results, dict) or isinstance(results, mp.managers.DictProxy)
assert results, "results shouldn't be empty"

def _format_time(seconds):
    minutes, seconds = divmod(float(seconds), 60)
    return f'{int(minutes):0>2}:{seconds:0>6.3f}'

# Print to result to console
for suite_name, suite_dict in results.items():
    print('Suite: ' + suite_name +
          ' Overall result: ' + suite_dict['result'].name +
          ' Overall time: ' + _format_time(suite_dict['time']) +
          ' Overall count: ' + str(suite_dict['count']) +
          ' Inc tags: ' + str(suite_dict['inc_tags']) +
          ' Exc tags: ' + str(suite_dict['exc_tags']))
    for test in suite_dict['tests']:
        print('Name: ' + test['name'] +
              ' Result: ' + test['result'].name +
              ' Time: ' + _format_time(test['time']) +
              ' Tags: ' + str(test['tags']))
    print()

# Produce xunit.xml
text = """<?xml version="1.0" encoding="UTF-8"?>
"""
for suite_name, suite_dict in results.items():
    text += f"""<testsuite classname="{suite_name}" tests="{suite_dict['count']['TOTAL']}"
                           errors="{suite_dict['count'][Result.TEST_ERROR]}"
                           failures="{suite_dict['count'][Result.FAILED]}"
                           skipped="0" time="{suite_dict['time']}">\n"""
    for test in suite_dict['tests']:
        text += f"""<testcase classname="{suite_name} - {test['name']}"
                              name="{test['name']}" time="{test['time']}">\n"""
        if test['result'] in [Result.FAILED, Result.TEST_ERROR]:
            text += """<failure message="test failed" type="AssertionError"></failure>\n"""
        text += "</testcase>\n"
    text += "</testsuite>\n"

text_file = open("test-results/xunit.xml", "w")
text_file.write(text)
text_file.close()

# Produce html report
text = """<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8" />
        <title>Test test framework report</title>
    </head>
    <body>
        <h1>Test Test Framework Report</h1>
"""
for suite_name, suite_dict in results.items():
    text += f"""
        <h2>{suite_name}</h2>
        <p>Result: {suite_dict['result'].name}</p>
        <p>Time: {_format_time(suite_dict['time'])}</p>
        <p>Test Count: {suite_dict['count']['TOTAL']}</p>
        <p>PASSED: {suite_dict['count'][Result.PASSED]}</p>
        <p>FAILED: {suite_dict['count'][Result.FAILED]}</p>
        <p>KNOWN_FAILURE: {suite_dict['count'][Result.KNOWN_FAILURE]}</p>
        <p>TEST_ERROR: {suite_dict['count'][Result.TEST_ERROR]}</p>
        <table>
            <tr>
               <th>Test name</th>
               <th>Result</th>
               <th>Time</th>
               <th>Tags</th>
            </tr>"""
    for test in suite_dict['tests']:
        text += f"""
            <tr>
                <td>{test['name']}</td>
                <td>{test['result'].name}</td>
                <td>{_format_time(test['time'])}</td>
                <td>{str(test['tags'])}</td>
            </tr>"""
    text += """
        </table>"""

text += """
    </body>
</html>"""

text_file = open("test-results/report.html", "w")
text_file.write(text)
text_file.close()

# Save test run to sqlite db
import sqlite3
con = sqlite3.connect('database.db')
cursor = con.cursor()
cursor.execute("""create table if not exists testRuns(
                    id integer primary key,
                    runDate text
                    );""")
con.commit()

cursor.execute("""create table if not exists suites(
                id integer primary key,
                testRunId integer,
                result char(50),
                time text,
                count integer,
                countPASSED integer,
                countFAILED integer,
                countKNOWN_FAILURE integer,
                countTEST_ERROR integer,
                inc_tags text,
                exc_tags text
                );""")
con.commit()

cursor.execute("""create table if not exists tests(
                id integer primary key,
                suiteId integer,
                result char(50),
                time text,
                tags text
                );""")
con.commit()

import datetime
cursor.execute(f'insert into testRuns (runDate) values ("{datetime.datetime.now()}");')
con.commit()

runID = cursor.lastrowid

for suite_name, suite_dict in results.items():
    cursor.execute(f'''insert into suites
                    (testRunId, result, time, count, inc_tags, exc_tags)
                    values
                    (
                        {runID},
                        "{suite_dict['result'].name}",
                        "{suite_dict['time']}",
                        {str(suite_dict['count']['TOTAL'])},
                        "{str(suite_dict['inc_tags'])}",
                        "{str(suite_dict['exc_tags'])}"
                    );''')
    suiteID = cursor.lastrowid
    for test in suite_dict['tests']:
        cursor.execute(f'''insert into tests (suiteId, result, time, tags) values
                        (
                            {suiteID},
                            "{test['result'].name}",
                            "{test['time']}",
                            "{str(test['tags'])}"
                        );''')
con.commit()
