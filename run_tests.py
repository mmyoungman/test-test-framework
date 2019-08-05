# Created by Mark Youngman on 05 August 2019
# Inspired by BitcoinTestFramework: https://github.com/bitcoin/bitcoin/blob/fa8a1d7ba30040f8c74f93fc41a61276c255a6a6/test/functional/test_framework/test_framework.py

from enum import Enum

class Result(Enum):
    PASSED = 1
    FAILED = 2
    KNOWN_FAILURE = 3

class TestFrameworkMetaClass(type):
    def __new__(cls, clsname, bases, dct):
        if not clsname == 'TestFramework':
            if not 'run_test' in dct:
                raise TypeError("TestFramework subclasses must override "
                                "'run_test'")
            if '__init__' in dct or 'main' in dct:
                raise TypeError("TestFramework subclasses may not override "
                                "'__init__' or 'main'"
        return super().__new__(cls, clsname, bases, dct)

class TestFramework(metaclass=TestFrameworkMetaClass):
    def __init__(self):
        pass

    def main(self):
        pass

    def run_test(self):
        """Tests must override this method to define test logic"""
        raise NotImplementedError
