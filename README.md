Common failures of test frameworks:
- Cannot get data on how well the test are performing
- Dilemma of letting failing tests fail or to comment them out

### Framework doesn't have X feature

This framework aims to be lightweight and simple. Rather than trying to provide every conceivable feature, this framework is designed to be extended. This means that anyone with some python experience should be able to inspect the framework's code and implement functionality to suite their project's particular needs. 

### Long run times

This test framework aims to provide the ability to run tests in parallel by default. The user is trusted to make sure test suites can run independently.

### No long-term record on the performance of tests

Record results over all test runs -- help to identify tests that offer poor ROI. Perhaps users can also mark real failures and false positives to provide greater insights.

### Don't let disabled tests be forgotten

More result types than pass and fail -- so a test can be "disabled" but still be run and provide information, even if it doesn't itself cause an entire test run to fail.

### Other potential features

The aim is only to provide the bare essential features by default, but here are other features that could be implemented:

- Rerun failed tests to protect against brittle tests.
