# Created by Mark Youngman on 30 March 2018

# TODO: 
# Record test pass/fail data to produce a report
# Make test runner include/exclude specified tags
# Record from what file a test was imported, so easier to find when it fails
# Have some way to run same test multiple times with different data?
# Record how long each test runs?

from os import listdir
from sys import exit

# Test result types
PASS = 0
FAIL = 1

class testSuite:
    def __init__(self, suiteName, location):
        self.name = suiteName
        self.location = location
        self.testArray = []
        self.testTagArray = []
        self.beforeSuiteFunc = lambda *args: None
        self.beforeTestFunc = lambda *args: None
        self.afterTestFunc = lambda *args: None
        self.afterSuiteFunc = lambda *args: None

    def addTest(self, testFunc, testTags):
        self.testArray.append(testFunc)
        self.testTagArray.append(testTags)

testSuiteArray = []
testSuiteArray.append(testSuite("firstTestSuite", "firstTestSuite"))
testSuiteArray.append(testSuite("anotherTestSuite", "anotherTestSuite"))

for ts in testSuiteArray:
    if not isinstance(ts, testSuite):
        exit(1)

    # test decorator
    def test(*tags):
        # If no test tags are specified, tags will be a test function
        if len(tags) == 1 and callable(tags[0]):
            ts.addTest(tags[0], [])
        else:
            def decorator(func):
                ts.addTest(func, [tag for tag in tags])
            return decorator
    
    # beforeSuite decorator
    def beforeSuite(func):
        ts.beforeSuiteFunc = func
    
    # beforeTest decorator
    def beforeTest(func):
        ts.beforeTestFunc = func
    
    # afterTest decorator
    def afterTest(func):
        ts.afterTestFunc = func
    
    # afterSuite decorator
    def afterSuite(func):
        ts.afterSuiteFunc = func
    
    # Import testSuite files
    for filename in sorted(listdir(ts.location)):
        #print("Found file: " + filename)
        if filename.endswith('.py'):
            exec(open(ts.location + "/" + filename).read())

    # Run the tests!
    print("Running Suite: " + ts.name)
    ts.beforeSuiteFunc()
    for i in range(len(ts.testArray)):
        ts.beforeTestFunc()
    
        if "happypath" in ts.testTagArray[i]:
            print(("Running Test: " + ts.testArray[i].__name__).ljust(60, '.'), end='')
            result = ts.testArray[i]()
            if result == PASS:
                print("\033[92mPASSED!\033[0m")
            elif result == FAIL:
                print("\033[91mFAILED!\033[0m")
            else:
                print("Something has gone seriously wrong!")
    
        ts.afterTestFunc()

    print()
    ts.afterSuiteFunc()
