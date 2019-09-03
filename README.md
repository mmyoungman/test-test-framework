Common failures of test frameworks:

### Framework doesn't have X feature

Rather than trying to provide every conceivable feature, this framework is designed to be extended. This means that anyone with some python experience should be able to inspect the framework's code and implement functionality to suit their project's particular needs.

### Long run times

This test framework aims to provide the ability to run test suites in parallel by default. The user is trusted to make sure test suites can run independently.

### No record of past test results

Record results over all test runs -- help to identify tests that needlessly extend run time or offer poor ROI. Maybe users can also mark false positives to provide greater insights?

### Disabled tests are forgotten

More result types than pass and fail, so a test can be still run and provide information, even if it doesn't cause an entire test suite to fail. Real failures aren't lost amongst false positives.

## To do

- Keeping all test run results for comparison
- run_tests.py should return appropriate code depends on results
- further develop --quiet?
- Rerun failed tests to protect against brittle tests?
- Profiling produces single file for multiple suites
- Improve html report
- Improve xunit report - check format of time, actual failure messages, etc.
- Test framework against a real project
