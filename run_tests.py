# Created by Mark Youngman on 05 August 2019
# Inspired by BitcoinTestFramework: https://github.com/bitcoin/bitcoin/blob/fa8a1d7ba30040f8c74f93fc41a61276c255a6a6/test/functional/test_framework/test_framework.py

import sys
from os import listdir
from enum import Enum

class Result(Enum):
    PASSED = 0
    FAILED = 1
    KNOWN_FAILURE = 2

class TestInstance:
    def __init__(self, func):
        self.name = func.__name__
        self.func = func

class TestSuiteMetaClass(type):
    def __new__(cls, name, bases, body):
        if not name == 'TestSuite':
            if '__init__' in body:
                raise TypeError("TestSuite subclasses may not override '__init__'")
            if 'add_test' in body:
                raise TypeError("TestSuite subclasses may not override 'add_test'")
            if 'run_tests' in body:
                raise TypeError("TestSuite subclasses may not override 'run_tests'")
        return super().__new__(cls, name, bases, body)

class TestSuite(metaclass=TestSuiteMetaClass):
    def __init__(self):
        self.test_array = []

    # test decorator
    def test(func):
        print('test decorator called')
        test_inst = TestInstance(func)
        #self.add_test(test_inst)

    def add_test(test_inst):
        print('add_test called')
        # TODO(mark): Validate test_inst
        if not isInstance(test_inst, TestInstance):
            print(f'Cannot add test {test_inst} because it isn\'t a TestInstance object!')
            sys.exit(1)
        self.test_array.append(test_inst)

    def before_suite(self):
        pass

    def before_test(self):
        pass

    def after_test(self):
        pass

    def after_suite(self):
        pass

    def run_tests(self):
        self.before_suite()
        print('test_array: ', self.test_array)
        for test_func in self.test_array:
            self.before_test()
            print('test_func name: ', test_func.__name__)
            result = test_func()
            self.after_test()
        self.after_suite()

if __name__ == '__main__':
    # Import tests
    for filename in listdir('tests'):
        if filename.endswith('.py'):
            exec(open(f'tests/{filename}').read())

    print([test_suite.__name__ for test_suite in TestSuite.__subclasses__()])

    for test_suite in TestSuite.__subclasses__():
        test_suite().run_tests()
