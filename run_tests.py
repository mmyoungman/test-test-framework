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
parser.add_argument("-t", "--tags",
                    dest="tags",
                    nargs="?",
                    metavar="{tag(s)}",
                    help="specify tests you wish to run by tag")
args = parser.parse_args()


# Import tests
for filename in listdir('tests'):
    if filename.endswith('.py') and filename not in ['__init__.py', 'TestSuite.py']:
        filename = filename[:-3]
        print("file: ", filename)
        importlib.import_module('tests.' + filename)

print("Subclasses: ", TestSuite.__subclasses__())

#for filename in listdir('tests'):
#    if filename.endswith('.py'):
#        exec(open('tests/' + filename).read())


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
