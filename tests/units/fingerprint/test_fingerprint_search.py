# -*- coding: utf-8 -*-
# Copyright (C) 2014 Universidade de Aveiro, DETI/IEETA, Bioinformatics Group - http://bioinformatics.ua.pt/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from selenium.webdriver.common.by import By

from utils.testcases import MontraTestCase
from utils.data import MontraTestData as data


class FingerprintSearchTestCase(MontraTestCase):
    """
    This test will verify that the search for fingerprints feature is working properly.
    The test is divided in two parts:

        1- The test tries to perform a search using valid values previously inserted in a test fingerprint.
        The expected behaviour is to pass only if the search is able to find the test fingerprint.

        2- The test tries to perform a search using invalid values that were not inserted in a test fingerprint.
        The expected behaviour is to pass only if the search is not able to find the test fingerprint.
    """

    def test_fingerprint_search(self):

        user2 = data.users["user2"]

        # Login as user2
        self.utils.login(user2["username"], user2["password"])

        self.utils.open_community()

        count = self.utils.get_number_of_fingerprints()

        current_fingerprint_acronym = data.fingerprint_acronym + str(count)

        assert current_fingerprint_acronym in self.driver.page_source

        # Click Search (side bar)
        databases_menu_button = self.driver.find_element(By.ID, "databases")
        databases_menu_button.click()
        databases_menu_button.find_element(By.XPATH, '../../ul//a[text()[contains(., "Advanced Search")]]').click()

        # Perform a valid search and check that the fingerprint appears
        self.search_good_arguments(current_fingerprint_acronym)

        # Reset page
        self.driver.get(self.base_url)

        self.utils.open_community()

        # Click Search (side bar)
        databases_menu_button = self.driver.find_element(By.ID, "databases")
        databases_menu_button.click()
        databases_menu_button.find_element(By.XPATH, '../../ul//a[text()[contains(., "Advanced Search")]]').click()

        # Perform an invalid search and check that no fingerprint appears
        self.search_bad_arguments()

    def search_good_arguments(self, fingerprint_acronym):
        """
        This method performs a search in to existing fingerprints using values that were previously introduced
        in a test fingerprint.
        The expected behaviour is the following:
        - Goes to the search page
        - Fills Page 1 fields and searches
        - Verifies that the search worked by confirming that the test fingerprint is listed
        - Verifies that the bottom panel shows a tooltip for each searched field
        - Clicks on "Refine Search" to test other pages as well
        - Repeats the previous four steps using Page 2
        - For Pages 4, 5 and 6 it will fill the three pages before searching again
        """
        # Fill some fields and click "Search"

        questions = [
            "question_nr_1.01", "question_nr_1.02", "question_nr_1.03", "question_nr_1.04", "question_nr_1.05",
            "question_nr_1.06", "question_nr_1.07.01", "question_nr_1.07.02", "question_nr_1.07.03",
            "question_nr_1.07.04", "question_nr_1.08.01", "question_nr_1.08.02", "question_nr_1.08.03",
            "question_nr_1.08.04", "question_nr_1.09.01", "question_nr_1.09.02", "question_nr_1.09.03",
            "question_nr_1.09.04", "question_nr_1.10.01", "question_nr_1.10.02",
            "question_nr_1.10.03", "question_nr_1.10.04"]

        # Page 1
        self.driver.find_element(By.ID, "question_1.01").send_keys(fingerprint_acronym)
        self.driver.find_element(By.ID, "question_1.02").send_keys(data.fingerprint_name)
        self.driver.find_element(By.ID, "question_1.03").send_keys(data.fingerprint_institution)
        self.driver.find_element(By.ID, "question_1.04").send_keys("test question_1.04")
        self.driver.find_element(By.ID, "question_1.05").send_keys("http://test105.com")
        self.driver.find_element(By.ID, "question_1.06").send_keys("http://test106.com")
        self.driver.find_element(By.ID, "question_1.07.01").send_keys("test question_1.07.01")
        self.driver.find_element(By.ID, "question_1.07.02").send_keys("test question_1.07.02")
        self.driver.find_element(By.ID, "question_1.07.03").send_keys("test10703@ua.random")
        self.driver.find_element(By.ID, "question_1.07.04").send_keys("test question_1.07.04")
        self.driver.find_element(By.ID, "question_1.08.01").send_keys("test question_1.08.01")
        self.driver.find_element(By.ID, "question_1.08.02").send_keys("test question_1.08.02")
        self.driver.find_element(By.ID, "question_1.08.03").send_keys("test10803@ua.random")
        self.driver.find_element(By.ID, "question_1.08.04").send_keys("test question_1.08.04")
        self.driver.find_element(By.ID, "question_1.09.01").send_keys("test question_1.09.01")
        self.driver.find_element(By.ID, "question_1.09.02").send_keys("test question_1.09.02")
        self.driver.find_element(By.ID, "question_1.09.03").send_keys("test10903@ua.random")
        self.driver.find_element(By.ID, "question_1.09.04").send_keys("test question_1.09.04")
        self.driver.find_element(By.ID, "question_1.10.01").send_keys("test question_1.10.01")
        self.driver.find_element(By.ID, "question_1.10.02").send_keys("test question_1.10.02")
        self.driver.find_element(By.ID, "question_1.10.03").send_keys("test11003@ua.random")
        self.driver.find_element(By.ID, "question_1.10.04").send_keys("test question_1.07.04")

        # Click "Search" button
        self.driver.find_element(By.XPATH, "//div[@id='qs_1']/div[6]/div[2]/button").click()

        # Check that the fingerprint appears
        assert "1 results found" in self.driver.page_source

        # Check that the bottom plugin exists and contains relevant information
        for question_nr in questions:
            assert question_nr in self.driver.page_source

        # Click "Refine Search" button
        self.driver.find_element(By.XPATH, "//button[contains(.,'Refine Search')]").click()

        # Click "Next" button
        self.driver.find_element(By.XPATH, "(//a[contains(text(),'Next')])[2]").click()

        # Page 2
        self.driver.find_element(By.ID, "question_2.01").send_keys("test question_2.01")

        self.driver.find_element(By.NAME, "question_2.02_more1").send_keys("test question_2.02_more1")
        self.driver.find_element(By.ID, "question_2.02_multiple_2").click()
        self.driver.find_element(By.ID, "question_2.02_multiple_6").click()

        self.driver.find_element(By.NAME, "question_2.05_more1").send_keys("test question_2.05_more1")
        self.driver.find_element(By.ID, "question_2.03_yes").click()
        self.driver.find_element(By.ID, "question_2.04_2").click()
        self.driver.find_element(By.ID, "question_2.05_multiple_1").click()
        self.driver.find_element(By.ID, "question_2.05_multiple_4").click()

        questions += ["question_nr_2.01", "question_nr_2.02", "question_nr_2.05"]

        # Click "Search" button
        self.driver.find_element(By.XPATH, "//div[@id='qs_2']/div[5]/div[2]/button").click()

        # Check that the fingerprint appears
        assert "1 results found" in self.driver.page_source

        # Check that the bottom plugin exists and contains relevant information
        for question_nr in questions:
            assert question_nr in self.driver.page_source

        # Click "Refine Search" button
        self.driver.find_element(By.XPATH, "//button[contains(.,'Refine Search')]").click()

        # Click Next Button
        # Page 1 to Page 2
        self.driver.find_element(By.XPATH, "(//a[contains(text(),'Next')])[2]").click()
        # Page 2 to Page 4 (Page 3 doesn't exist)
        self.driver.find_element(By.XPATH, "(// a[contains(text(), 'Next')])[4]").click()

        # Page 4
        self.driver.find_element(By.ID, "question_4.01").send_keys("test question_4.01")
        self.driver.find_element(By.NAME, "question_4.04_more1").send_keys("test question_4.04_more1")
        self.driver.find_element(By.CSS_SELECTOR, "#answer_4\\.04 li:nth-child(2) .checkbox-label").click()
        self.driver.find_element(By.ID, "question_4.05").send_keys("test question_4.05")
        self.driver.find_element(By.ID, "question_4.06").send_keys("test question_4.06")
        self.driver.find_element(By.ID, "question_4.07").send_keys("test question_4.07")

        questions += ["question_nr_4.01", "question_nr_4.04", "question_nr_4.05",
                      "question_nr_4.06", "question_nr_4.07"]

        # Click "Next" button
        # Page 4 to Page 5
        self.driver.find_element(By.XPATH, "(//a[contains(text(),'Next')])[6]").click()

        # Page 5
        self.driver.find_element(By.CSS_SELECTOR, "#answer_5\\.01 li:nth-child(2) .radiobox-label").click()

        self.driver.find_element(
            By.CSS_SELECTOR, "#answer_5\\.02 .questionnaire-choice-checkbox > .radiobox-label").click()
        self.driver.find_element(By.ID, "question_5.03").send_keys("test question_5.03")
        self.driver.find_element(By.ID, "question_5.04").send_keys("3.5")
        self.driver.find_element(By.ID, "question_5.05").send_keys("test question_5.05")
        self.driver.find_element(By.ID, "question_5.06").send_keys("test question_5.06")
        self.driver.find_element(By.ID, "question_5.07").send_keys("test question_5.07")

        self.driver.find_element(By.ID, "question_5.11").send_keys("test question_5.11")
        self.driver.find_element(By.ID, "question_5.08_yes").click()
        self.driver.find_element(By.CSS_SELECTOR, "#answer_5\\.09 li:nth-child(2) .radiobox-label").click()
        self.driver.find_element(
            By.CSS_SELECTOR, "#answer_5\\.10 .questionnaire-choice-checkbox > .radiobox-label").click()

        questions += ["question_nr_5.01", "question_nr_5.03", "question_nr_5.04", "question_nr_5.05",
                      "question_nr_5.06", "question_nr_5.07", "question_nr_5.08", "question_nr_5.11"]

        # Click "Next" button
        # Page 5 to Page 6
        self.driver.find_element(By.XPATH, "(// a[contains(text(), 'Next')])[8]").click()

        # Page 6
        self.driver.find_element(By.ID, "question_6.03").send_keys("test question_6.03\ntest question_6.03")
        questions += ["question_nr_6.03"]

        # Click "Search" button
        self.driver.find_element(By.XPATH, "// div[ @ id = 'qs_6'] / div[5] / div[2] / button").click()

        # Check that the fingerprint appears
        assert "1 results found" in self.driver.page_source

        # Check that the bottom plugin exists and contains relevant information
        for question_nr in questions:
            assert question_nr in self.driver.page_source

    def search_bad_arguments(self):
        """
        This method performs a search in to existing fingerprints using invalid values that were not previously
         introduced in a test fingerprint. The idea here is to test if the search works properly for invalid searches
        The expected behaviour is the following:
        - Goes to the search page
        - Fills one Page 1 field with wrong data and searches
        - Verifies that the search worked by confirming that the test fingerprint is not listed
        - Verifies that the bottom panel shows a tooltip for each searched field
        - Clicks on "Refine Search" to test other pages as well
        - Cleans previously filled fields
        - Repeats the previous four steps using Page 2
        """

        # Page 1
        self.driver.find_element(By.ID, "question_1.01").send_keys("Dummy fingerprint")
        questions = ["question_nr_1.01"]

        # Click "Search" button
        self.driver.find_element(By.XPATH, "//div[@id='qs_1']/div[6]/div[2]/button").click()

        # Check that the fingerprint does not appears
        assert "No results found" in self.driver.page_source

        # Check that the bottom plugin exists and contains relevant information
        for question_nr in questions:
            assert question_nr in self.driver.page_source

        # Click "Refine Search" button
        self.driver.find_element(By.XPATH, "//button[contains(.,'Refine Search')]").click()

        # Clean the Page 1 filled field
        self.driver.find_element(By.ID, "question_1.01").send_keys("")

        # Click "Next" button
        self.driver.find_element(By.XPATH, "(//a[contains(text(),'Next')])[2]").click()

        # Page 2
        self.driver.find_element(By.ID, "question_2.01").send_keys("dummy")

        questions = ["question_nr_2.01"]

        # Click "Search" button
        self.driver.find_element(By.XPATH, "//div[@id='qs_2']/div[5]/div[2]/button").click()

        # Check that the fingerprint does not appears
        assert "No results found" in self.driver.page_source

        # Check that the bottom plugin exists and contains relevant information
        for question_nr in questions:
            assert question_nr in self.driver.page_source
