from selenium import webdriver
from .TestSuite import *

class SeleniumTestSuite2(TestSuite):
    def before_suite(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://mark.youngman.info")

    def after_suite(self):
        self.driver.close()

    @TestSuite.test
    def click_about_link(self):
        self.driver.find_element_by_xpath('//a[text()="About"]').click()
        return Result.PASSED

    @TestSuite.test('ignore')
    def click_aws_cert_link(self):
        self.driver \
            .find_element_by_xpath('//a[text()="AWS Certified Developer - Associate"]') \
            .click()
        call_a_function_that_does_not_exist()
        return Result.PASSED
