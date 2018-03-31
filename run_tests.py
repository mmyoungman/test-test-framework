# Created by Mark Youngman on 30 March 2018

# TODO: 
# Record test pass/fail data to produce a report
# Record from what file a test was imported, so easier to find when it fails
# Have some way to run same test multiple times with different data?
# Record how long each test runs?

from os import listdir
import sys

tagsInclude = []
tagsExclude = []

# Handle arguments
for i in range(1, len(sys.argv)):
    if sys.argv[i].startswith("include="):
        tags = sys.argv[i].split("=")[1]
        for tag in tags.split(","):
            tagsInclude.append(tag)
    elif sys.argv[i].startswith("exclude="):
        tags = sys.argv[i].split("=")[1]
        for tag in tags.split(","):
            tagsExclude.append(tag)

# Test result types
PASS = 0
FAIL = 1

# Hack to record which file a test is found
testLocation = ""

class test_inst:
    def __init__(self, func, location, tags=[], data=[]): 
        self.func = func
        self.location = location
        self.tags = tags
        self.data = data

class testSuite:
    def __init__(self, suiteName, location):
        self.name = suiteName
        self.location = location
        self.testArray = []
        self.beforeSuiteFunc = lambda *args: None
        self.beforeTestFunc = lambda *args: None
        self.afterTestFunc = lambda *args: None
        self.afterSuiteFunc = lambda *args: None

testSuiteArray = []
testSuiteArray.append(testSuite("firstTestSuite", "firstTestSuite"))
testSuiteArray.append(testSuite("anotherTestSuite", "anotherTestSuite"))

for ts in testSuiteArray:
    if not isinstance(ts, testSuite):
        sys.exit(1)

    # test decorator
    def test(*tags):
        # If no test tags are specified, tags will be a test function
        if len(tags) == 1 and callable(tags[0]):
            if tags[0].__name__ == "test":
                print("ERROR: Test function cannot be named \"test\"!")
                sys.exit(1)
            ts.testArray.append(test_inst(tags[0], testLocation))
        else:
            def decorator(func):
                ts.testArray.append(test_inst(func, testLocation, [tag for tag in tags]))
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
        if filename.endswith('.py'):
            testLocation = ts.location + "/" + filename
            exec(open(testLocation).read())

    # Run the suite
    print("Running Suite: " + ts.name)
    ts.beforeSuiteFunc()
    for i in range(len(ts.testArray)):

        # Determine whether to skip current test
        skip = True
        if len(tagsInclude) == 0 or (len(tagsInclude) == 1 and tagsInclude[0] == ''):
            skip = False
        for tag in ts.testArray[i].tags:
            if tag in tagsInclude:
                skip = False
        for tag in ts.testArray[i].tags:
            if tag in tagsExclude:
                skip = True
                break

        if not skip:
            # Run the test
            ts.beforeTestFunc()
            print(("Running Test: " + ts.testArray[i].func.__name__).ljust(60, '.'), end='')
            result = ts.testArray[i].func()
            if result == PASS:
                print("\033[92mPASSED!\033[0m")
            elif result == FAIL:
                print("\033[91mFAILED!\033[0m")
            else:
                print("Something has gone seriously wrong!")
            print("Test found at: " + ts.testArray[i].location)
            ts.afterTestFunc()

    ts.afterSuiteFunc()
    print()
