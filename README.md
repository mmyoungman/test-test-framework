Possible Test Framework Features
================================

Common failures of test frameworks:
- Long run times.
- Difficult to manage failures that cannot be quickly fixed.
- Cannot get information on the ROI of particular tests.

Parallelism: gives options to speed up test runs. Expect users to design tests with parallelism in mind.
Extensible: easy to understand code makes the framework easy to extend to a user's specific needs.
Lightweight: 

* Record passes and failures over multiple runs of the all tests -- helps to identify tests that offer poor ROI.

* A test must fail twice before it is marked as a failure -- guard against unreliable tests.

* More result types than pass and fail -- so a test can be "disabled" but still be run and provide information, even if it doesn't itself cause an entire test run to fail.

* Make parallelism easy to do.
