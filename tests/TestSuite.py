from enum import Enum
import timeit

class Result(Enum):
    PASSED = 0
    FAILED = 1
    KNOWN_FAILURE = 2
    TEST_ERROR = 3

class TestSuiteMetaClass(type):
    def __new__(cls, name, bases, body):
        if name != 'TestSuite':
            for method_name in ['__init__', 'run_tests', '_do_nothing',
                                '_format_time', '_update_suite_result']:
                if method_name in body:
                    raise TypeError("TestSuite subclasses may not override '" + method_name + "'")
        return super().__new__(cls, name, bases, body)

class TestSuite(metaclass=TestSuiteMetaClass):
    def __init__(self, quiet):
        self.tests_to_run = []

        if quiet:
            self.print = self._do_nothing  # no lambda because of multiprocessing's pickling!
        else:
            self.print = print

    def _do_nothing(self, *args):
        pass

    def test(*tags):
        if len(tags) == 1 and callable(tags[0]):
            test_func = tags[0]
            test_func.is_test = True
            test_func.tags = []
            return test_func
        else:
            for tag in tags:
                assert isinstance(tag, str)
            def decorator(test_func):
                test_func.is_test = True
                test_func.tags = [tag for tag in tags]
                return test_func
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
        self.print('Running ' + self.__class__.__name__ + '...')

        # Get tests to run
        method_name_list = dir(self)
        for name in method_name_list:
            method = getattr(self, name)
            if hasattr(method, 'is_test'):
                assert hasattr(method, 'tags')

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

        # Test run prep
        def _update_suite_result(current, result):
            if current is Result.FAILED or result is Result.FAILED:
                return Result.FAILED
            elif result is Result.TEST_ERROR:
                return Result.TEST_ERROR
            elif result is Result.KNOWN_FAILURE and current is not Result.TEST_ERROR:
                return Result.KNOWN_FAILURE
            else:
                return Result.PASSED

        def _results_count(new_result, result_list):
            result_list[0] += 1
            if new_result is Result.PASSED:
                result_list[1] += 1
            elif new_result is Result.FAILED:
                result_list[2] += 1
            elif new_result is Result.KNOWN_FAILURE:
                result_list[3] += 1
            elif new_result is Result.TEST_ERROR:
                result_list[4] += 1
            else:
                assert False, "new_result isn't a supported Result type!"
            return result_list

        def _format_time(seconds):
            minutes, seconds = divmod(seconds, 60)
            return f'{int(minutes):0>2}:{seconds:0>6.3f}'

        suite_overall_result = Result.PASSED
        suite_results = []
        suite_start_time = timeit.default_timer()
        suite_result_count = [0, 0, 0, 0, 0]

        # Run the tests
        assert len(self.tests_to_run) > 0
        self.before_suite()

        for test in self.tests_to_run:
            self.before_test()

            test_start_time = timeit.default_timer()
            try:
                test_result = test()
            except Exception as e:
                test_result = Result.TEST_ERROR
                self.print("Test exception:", test.__name__, e)
            test_run_time = timeit.default_timer() - test_start_time
            assert isinstance(test_result, Result), test.__name__ + ' returned result should be type(Result)'

            suite_overall_result = _update_suite_result(suite_overall_result, test_result)
            suite_result_count = _results_count(test_result, suite_result_count)
            suite_results.append({
                'name': test.__name__,
                'result': test_result,
                'time': _format_time(test_run_time),
                'tags': test.tags,
            })

            test_name_justified = (self.__class__.__name__ + ": " + test.__name__).ljust(60, '.')
            self.print(test_name_justified + test_result.name + '!')

            self.after_test()

        self.after_suite()
        suite_run_time = timeit.default_timer() - suite_start_time
        results[self.__class__.__name__] = {
            'time': _format_time(suite_run_time),
            'tests': suite_results,
            'result': suite_overall_result,
            'count': suite_result_count,
            'inc_tags': inc_tags,
            'exc_tags': exc_tags
        }
        self.print('Finished ' + self.__class__.__name__)
