# Test result types
PASS = 0
FAIL = 1

class testSuite:
    name = ""
    location = ""
    testArray = []
    testTagArray = []
    beforeSuiteFunc = None
    beforeTestFunc = None
    afterTestFunc = None
    afterSuiteFunc = None

    def __init__(self, suiteName, location):
        self.name = suiteName
        self.location = location

    def addTest(self, testFunc, testTags):
        self.testArray.append(testFunc)
        self.testTagArray.append(testTags)

ts = testSuite("firstTestSuite", "firstTestSuite")

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


@test
def testOne():
    #print("testOne prints this when it passes!")
    return PASS
   #print("testTest prints this when it fails!")

@test("blah", "happypath", "another")
def testTwo():
    #print("testTwo prints this when it passes!")
    return PASS
   #print("testTest prints this when it fails!")

@test("something else", "happypath")
def testThree():
    #print("testThree prints this when it passes!")
    return PASS
   #print("testTest prints this when it fails!")

# Run the tests!
print("Running " + ts.name)
if ts.beforeSuiteFunc != None:
    ts.beforeSuiteFunc()
for i in range(len(ts.testArray)):
    if ts.beforeTestFunc != None:
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

    if ts.afterTestFunc != None:
        ts.afterTestFunc()

if ts.afterSuiteFunc != None:
    ts.afterSuiteFunc()

print(ts.testArray)
print(ts.testTagArray)
