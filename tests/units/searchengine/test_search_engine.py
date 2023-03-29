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
from selenium.webdriver.common.keys import Keys

from utils.testcases import MontraTestCase
from utils.data import MontraTestData as data


class SearchEngineTestCase(MontraTestCase):
    """
    This test will verify that the search for free text feature is working properly.
    The test is divided in three parts:

        1- The test tries to perform a search using valid values. The expected
        behaviour is to pass only if the search is able to find previously inserted elements that were indexed.

        2- The test tries to perform a search using invalid values. The expected behaviour is to pass only if the
        search is not able to find anything.

        3- In order to test the feature, the user will be removed from the community and the valid search will be
        repeated. The expected behaviour is to pass only if the search is not able to find anything since the user
        does not belong to the test community anymore.
    """

    def test_search_engine(self):

        user1 = data.users["user1"]

        # Login as user1
        self.utils.login(user1["username"], user1["password"])

        # Part 1
        # Search for valid words
        valid_search_words = ['test', 'fingerprint', 'Aveiro', 'institution', '2.01', '4.01']
        self.search_words(valid_search_words, True)

        # Part 2
        # Search for invalid words
        invalid_search_words = ['dummy', 'doe']
        self.search_words(invalid_search_words, False)

        # Part 3

        # Remove user1 from community
        self.utils.logout()
        self.utils.comm_user_remove()

        # Login as user1
        self.utils.login(user1["username"], user1["password"])

        # Try to perform valid searches
        # It should not work since the user can't see anything from the community anymore
        self.search_words(valid_search_words, False)

        # Add user to community to keep db state
        self.utils.logout()
        self.utils.comm_user_add()

    def search_words(self, words, valid=True):
        """
        This method will search for the given words using the free text searching feature.
        Args:
            words: list of words to search for
            valid: whether the search should return results or not
        """
        for word in words:
            # Click the search box
            self.driver.find_element(By.ID, "edit-search-block-form--3").click()

            # Clear the text box area
            self.driver.find_element(By.ID, "edit-search-block-form--3").clear()
            # Type a word
            self.driver.find_element(By.ID, "edit-search-block-form--3").send_keys(word)

            # Click enter
            self.driver.find_element(By.ID, "edit-search-block-form--3").send_keys(Keys.RETURN)

            # Check that the result is valid
            if valid:
                assert "No results found" not in self.driver.page_source
            else:
                assert "No results found" in self.driver.page_source
