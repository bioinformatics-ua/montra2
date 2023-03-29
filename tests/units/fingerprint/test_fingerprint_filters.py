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

from datetime import date, timedelta, datetime
from selenium.webdriver.common.by import By

from utils.testcases import MontraTestCase
from utils.data import MontraTestData as data


class FingerprintFilterTestCase(MontraTestCase):
    """
    This test will verify that the fingerprint filtering feature is working properly.
    Namely, it will test the following features:

    1 - Filter using different fields. Namely:
    1.a - Name
    1.b - Institution name
    1.c - Last update

    2 - Verify that the filtering is returning expected entries

    3 - Verify that the list of applied filters is being rendered properly .
    """

    def test_fingerprint_filters(self):

        user2 = data.users["user2"]

        # Login with user2, who has permissions
        self.utils.login(user2["username"], user2["password"])

        # Open the TEST community
        self.utils.open_community()

        # Get Last Update date
        date_elem = self.driver.find_element(By.CSS_SELECTOR, ".table-row:nth-child(2) > .date")
        date_obj = datetime.strptime(date_elem.text, "%Y-%m-%d").date()

        filters = [('Name', data.fingerprint_name, True),
                   ('Institution name', data.fingerprint_institution, True),
                   ('Last Update', date_obj, True),
                   ('Name', 'dummy_name', False),
                   ('Institution name', 'dummy_institution', False),
                   ('Last Update', date_obj - timedelta(days=15), False)]

        self.filter_all_fields(filters=filters)

    def filter_all_fields(self, filters):
        """
        This method will test given filters with given values.
        It has two possible interactions:

        1 - Using text fields

        2 - Using date fields

        Each interaction is performed in separate methods
        Args:
            filters: list containing the tuples (filter_name, value, valid).
        """
        # Go to the main page
        self.driver.get(self.base_url)

        # Open the TEST community
        self.utils.open_community()

        # For each filter, perform a search
        for i, f in enumerate(filters):
            filter_name = f[0]
            value = f[1]
            valid = f[2]

            if i != 0:  # When the page is first loaded no filters are applied, so the Clear all button is hidden.
                # Click "Clear All"
                self.driver.find_element(By.ID, "clear-filter-btn").click()

            # Click "Filters/Order By"
            self.driver.find_element(By.XPATH, "//a[contains(.,' Filters /  Order By')]").click()

            # Test the current field. Texts have a different interaction than dates.
            if isinstance(value, date):
                self.filter_date(filter_name, value, valid)
            else:
                self.filter_text(filter_name, value, valid)

    def filter_text(self, filter_name, value, valid):
        """
        This method will test a given text filter.
        The expected behavior is as follows:
        1 - It will verify that the filter's name is listed in the filter pop-up.

        2 - It will fill the filter's text box with the given value

        3 - It will verify that the result of the filter is being rendered and it has the expected value

        4 - It will verify if the filter is being listed in the top bar cards (Filtered by :)

        Args:
            filter_name (str): A text filter to be tested
            value (str): The filter value
            valid (bool): Whether the filter as results or not
        """

        # Verify that the filter label exists
        label_element = self.driver.find_element(By.XPATH, "//label[contains(.,'{}')]".format(filter_name))
        assert label_element.is_enabled()

        # Get the correspondent div
        value_element_parent = label_element.find_element(By.XPATH, "..")
        value_element_parent_childs = value_element_parent.find_elements(By.XPATH, ".//*")

        value_element = None

        # Get the input correspondent for the current filter
        for child in value_element_parent_childs:
            if child.get_attribute("type") == 'text':
                value_element = child
                break

        assert value_element is not None

        # Write the filter's value
        value_element.send_keys(value)

        # Click "Apply"
        self.driver.find_element(By.XPATH, "// button[contains(., 'Apply')]").click()

        # Check that results are showing the expected value
        table = self.driver.find_element(By.ID, "table_content")

        if valid:
            date_element = table.find_element(By.XPATH, ".//tr / td[contains(., '{}')]".format(value))
            assert date_element.text == value
            assert "0 Results" not in self.driver.page_source
        else:
            assert "0 Results" in self.driver.page_source

        # Check that the top bar has the filters
        assert "Filtered by: {}".format(filter_name) in self.driver.page_source

    def filter_date(self, filter_name, value, valid):
        """
        This method will test a given date filter.
        The expected behavior is as follows:
        1 - It will verify that the filter's name is listed in the filter pop-up.

        2 - It will fill the filter's input box with the given value (date)

        3 - It will verify that the result of the filter is being rendered and it has the expected value

        Args:
            filter_name (str): A date filter to be tested
            value (date): The filter value
            valid (bool): Whether the filter as results or not
        """

        # Verify that the filter label exists
        label_element = self.driver.find_element(By.XPATH, "//label[contains(.,'{}')]".format(filter_name))
        assert label_element.is_enabled()

        # Test the last update field
        lue_parent = label_element.find_element(By.XPATH, "..")
        lue_parent_childs = lue_parent.find_elements(By.XPATH, ".//div / input")
        start = None
        stop = None
        for e in lue_parent_childs:
            if e.get_attribute("type") == 'date' and e.get_attribute("placeholder") == 'Start':
                start = e
            elif e.get_attribute("type") == 'date' and e.get_attribute("placeholder") == 'End':
                stop = e
        assert start is not None and stop is not None

        # Perform a search of fingerprints added since 01-01-2000 until filter value
        start.send_keys("01")
        start.send_keys("01")
        start.send_keys("2000")
        stop.send_keys(str(value.month).zfill(2))
        stop.send_keys(str(value.day).zfill(2))
        stop.send_keys(value.year)

        # Click "Apply"
        self.driver.find_element(By.XPATH, "// button[contains(., 'Apply')]").click()

        # Check that the result is showing
        table = self.driver.find_element(By.ID, "table_content")

        if valid:
            date_element = table.find_element(By.XPATH, ".//tr / td[contains(., '{}')]".format(value.__str__()))
            assert date_element.text == value.__str__()
            assert "0 Results" not in self.driver.page_source
        else:
            assert "0 Results" in self.driver.page_source
