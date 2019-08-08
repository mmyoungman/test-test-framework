# Created by Mark Youngman on 05 August 2019

from os import listdir
from enum import Enum

class Result(Enum):
    PASSED = 0
    FAILED = 1
    KNOWN_FAILURE = 2
    TEST_ERROR = 3

class TestSuiteMetaClass(type):
    def __new__(cls, name, bases, body):
        if name != 'TestSuite':
            if '__init__' in body:
                raise TypeError("TestSuite subclasses may not override '__init__'")
            if 'run_tests' in body:
                raise TypeError("TestSuite subclasses may not override 'run_tests'")
        return super().__new__(cls, name, bases, body)

class TestSuite(metaclass=TestSuiteMetaClass):
    def __init__(self):
        self.tests_to_run = []

    def before_suite(self):
        pass

    def before_test(self):
        pass

    def after_test(self):
        pass

    def after_suite(self):
        pass

    def run_tests(self):
        print('Running ' + self.__class__.__name__ + '...')

        method_name_list = dir(self)
        is_test = lambda name: name.startswith('test__')
        test_name_list = filter(is_test, method_name_list)
        for name in test_name_list:
            method = getattr(self, name)
            self.tests_to_run.append(method)

        self.before_suite()

        for test in self.tests_to_run:
            self.before_test()

            try:
                result = test()
            except:
                result = Result.TEST_ERROR

            test_name = test.__name__[6:]
            test_name_justified = test_name.ljust(60, '.')
            print(test_name_justified + result.name + '!')

            self.after_test()

        self.after_suite()

if __name__ == '__main__':
    # Import tests
    for filename in listdir('tests'):
        if filename.endswith('.py'):
            exec(open('tests/' + filename).read())

    for test_suite in TestSuite.__subclasses__():
        test_suite_inst = test_suite()
        test_suite_inst.run_tests()
