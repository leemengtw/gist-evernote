"""
This script uses a simplified version of the one here:
https://snipt.net/restrada/python-selenium-workaround-for-full-page-screenshot-using-chromedriver-2x/

It contains the *crucial* correction added in the comments by Jason Coutu.
"""

import sys
import time

from selenium import webdriver
import unittest

import util

class Test(unittest.TestCase):
    """ Demonstration: Get Chrome to generate fullscreen screenshot """

    def setUp(self):
        self.driver = webdriver.Chrome()

    def tearDown(self):
        self.driver.quit()

    def test_fullpage_screenshot(self):
        ''' Generate document-height screenshot '''
        url = "https://gist.github.com/leemengtaiwan/e393d881222885f59ef09a14117159c8"
        self.driver.get(url)
        time.sleep(5)
        util.fullpage_screenshot(self.driver, "test.png")


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0]])