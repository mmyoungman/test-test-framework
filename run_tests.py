import os

# Test result types
PASS = 0
FAIL = 1

class testSuite:
    name = ""
    location = ""
    testArray = []
    testTagArray = []
    beforeSuiteFunc = lambda *args: None
    beforeTestFunc = lambda *args: None
    afterTestFunc = lambda *args: None
    afterSuiteFunc = lambda *args: None

    def __init__(self, suiteName, location):
        self.name = suiteName
        self.location = location

    def addTest(self, testFunc, testTags):
        self.testArray.append(testFunc)
        self.testTagArray.append(testTags)

testSuiteArray = []
testSuiteArray.append(testSuite("firstTestSuite", "firstTestSuite"))

for ts in testSuiteArray:
    #print(type(ts))
    if not isinstance(ts, testSuite):
        os.exit(1)

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
    
    for filename in sorted(os.listdir(ts.location)):
        #print(filename)
        if filename.endswith('.py'):
            exec(open(ts.location + "/" + filename).read())
    
    # Run the tests!
    print("Running " + ts.name)
    ts.beforeSuiteFunc()
    for i in range(len(ts.testArray)):
        ts.beforeTestFunc()
    
        if "happypath" in ts.testTagArray[i]:
            print("Running " + ts.testArray[i].__name__ + "...")
            result = ts.testArray[i]()
            if result == PASS:
                print("PASSED!")
            elif result == FAIL:
                print("FAILED!")
            else:
                print("Something has gone seriously wrong!")
    
        ts.afterTestFunc()
    
    ts.afterSuiteFunc()
    
    #print(ts.testArray)
    #print(ts.testTagArray)
