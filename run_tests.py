# Created by Mark Youngman on 05 August 2019
# Inspired by BitcoinTestFramework: https://github.com/bitcoin/bitcoin/blob/fa8a1d7ba30040f8c74f93fc41a61276c255a6a6/test/functional/test_framework/test_framework.py

from enum import Enum

class Result(Enum):
    PASSED = 0
    FAILED = 1
    KNOWN_FAILURE = 2

class TestSuiteMetaClass(type):
    def __new__(cls, name, bases, body):
        if not name == 'TestFramework':
            if not 'run_test' in body:
                raise TypeError("TestFramework subclasses must override "
                                "'run_test'")
            if '__init__' in body or 'main' in body:
                raise TypeError("TestFramework subclasses may not override "
                                "'__init__' or 'main'")
        return super().__new__(cls, name, bases, body)

class TestSuite(metaclass=TestSuiteMetaClass):
    def __init__(self):
        pass

    def main(self):
        pass

    def before_suite(self):
        pass

    def before_test(self):
        pass

    def run_tests(self):
        """Tests must override this method to define test logic"""
        raise NotImplementedError

    def after_test(self):
        pass

    def after_suite(self):
        pass
