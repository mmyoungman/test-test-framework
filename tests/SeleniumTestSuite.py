from selenium import webdriver
from time import sleep

class SeleniumTestSuite(TestSuite):
    def before_suite(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://mark.youngman.info")

    def after_suite(self):
        self.driver.close()

    def tests(self):
        self.add_test(self.click_about_link)
        self.add_test(self.click_aws_cert_link)

    def click_about_link(self):
        self.driver.find_element_by_xpath('//a[text()="About"]').click()
        return Result.PASSED

    def click_aws_cert_link(self):
        self.driver.find_element_by_xpath('//a[text()="AWS Certified Developer - Associate"]').click()
        sleep(3)
        return Result.PASSED


