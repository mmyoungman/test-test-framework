# Created by Mark Youngman on 05 August 2019
# Inspired by BitcoinTestFramework: https://github.com/bitcoin/bitcoin/blob/fa8a1d7ba30040f8c74f93fc41a61276c255a6a6/test/functional/test_framework/test_framework.py

from enum import Enum

class Result(Enum):
    PASSED = 0
    FAILED = 1
    KNOWN_FAILURE = 2

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

    def add_test(self, test_func):
        self.test_array.append(test_func)

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
        for test_func in self.test_array:
            self.before_test()
            result = test_func()
            self.after_test()
        self.after_suite()

if __name__ == '__main__':
    print([test_suite.__name__ for test_suite in TestSuite.__subclasses__()])
