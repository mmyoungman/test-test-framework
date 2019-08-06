from selenium import webdriver
from time import sleep

class SeleniumTestSuite(TestSuite):
    def before_suite(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://mark.youngman.info")
        sleep(2)

    def after_suite(self):
        self.driver.close()

    @TestSuite.test
    def click_about_link():
        self.driver.find_element_by_xpath('//a[text()="About"]').click()
        sleep(10)
