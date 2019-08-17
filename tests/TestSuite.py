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
        
    def test(*tags):
        # If no tags specified, tags variable contains the function being decorated!
        if len(tags) == 1 and callable(tags[0]):
            tags[0].is_test = True
            tags[0].tags = []
            return tags[0]
        def decorator(func):
            def wrapper(cls_instance):
                return func(cls_instance)
            wrapper.is_test = True
            wrapper.tags = [tag for tag in tags]
            wrapper.__name__ = func.__name__
            return wrapper
        return decorator

    def before_suite(self):
        pass

    def before_test(self):
        pass

    def after_test(self):
        pass

    def after_suite(self):
        pass

    def run_tests(self, results, inc_tags=[], exc_tags=[]):
        print('Running ' + self.__class__.__name__ + '...')

        # Get tests to run
        method_name_list = dir(self)
        for name in method_name_list:
            method = getattr(self, name)
            if hasattr(method, 'is_test'):
                assert(hasattr(method, 'tags'))

                # Skip tests to be excluded by tag
                should_ignore = False
                for method_tag in method.tags:
                    if method_tag in exc_tags:
                        should_ignore = True
                        break
                if should_ignore:
                    continue

                # Include tests to be included by tag
                if inc_tags == []:
                    self.tests_to_run.append(method)
                else:
                    for method_tag in method.tags:
                        if method_tag in inc_tags:
                            self.tests_to_run.append(method)
                            break

        # Run the tests
        suite_results = []
        self.before_suite()

        for test in self.tests_to_run:
            self.before_test()

            try:
                result = test()
            except Exception as e:
                result = Result.TEST_ERROR
                print("Test exception:", test.__name__, e)

            suite_results.append([test.__name__, result.name])

            test_name_justified = (self.__class__.__name__ + ": " + test.__name__).ljust(60, '.')
            print(test_name_justified + result.name + '!')

            self.after_test()

        self.after_suite()
        results[self.__class__.__name__] = suite_results
        print('Finished ' + self.__class__.__name__)
