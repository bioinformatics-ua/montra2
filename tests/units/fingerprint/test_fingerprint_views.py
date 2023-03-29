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

import os
import time
from selenium.webdriver.common.by import By

from utils.testcases import MontraTestCase
from utils.data import MontraTestData as data


class FingerprintViewsTestCase(MontraTestCase):
    """
    This test will verify that the Fingerprint views feature is working properly.
    The views to be tested are:

    1 - List view

    2 - Table view

    3 - Card view
    """

    def test_fingerprint_views(self):

        user2 = data.users["user2"]

        # Login with user2, who has permissions
        self.utils.login(user2["username"], user2["password"])

        # Select fields for views
        self.select_view_fields()

        # Test the Table View
        self.table_view()

        # Test the List view
        self.list_view()

        # # Test the Card View
        self.card_view()

    def select_view_fields(self):
        """
        This method will setup the fields that will appear on each view.
        For each view, the fingerprint name and institution name will be used.
        The expected behavior is as follows:
        - Goes to the landing page.
        - Opens the Test community.
        - Opens the left-most questionnaire since it's the one that the fingerprints are using.
        - Selects "Manage" from the navigation bar
        - Selects "Settings" from the navigation bar
        - Selects "List View" tab
        - Selects fields "name" and "institution name"
        - Clicks on "Save"
        - Repeats the 2 previous steps for tabs "Table View" and "Card View" , selecting the fields for each section
        """
        # Go to the main page
        self.driver.get(self.base_url)

        # Open the TEST community
        self.utils.open_community()

        # Click on "Manage"
        element_to_scroll = self.driver.find_element(By.ID, "mancomm")
        self.driver.execute_script("arguments[0].scrollIntoView();", element_to_scroll)
        element_to_scroll.click()

        # Click on "Views"
        element_to_scroll.find_element(By.XPATH, '../../ul//a[text()[contains(., "Views")]]').click()

        # Click on "Table View" tab
        self.driver.find_element(By.LINK_TEXT, "Table View").click()
        # Click on "1.02 Name" and "1.03 Institution name" fields
        self.driver.find_element(By.XPATH, "//li[contains(.,'1.02 Name')]").click()
        self.driver.find_element(By.XPATH, "//li[contains(.,'1.03 Institution name')]").click()
        # Click on "Save"
        self.driver.find_element(By.XPATH, "//button[contains(.,'  Save')]").click()

        # Click on "List View" tab
        self.driver.find_element(By.LINK_TEXT, "List View").click()
        # Section 0
        # Click on "1.02 Name" field
        self.driver.find_element(By.CSS_SELECTOR, "#field_selector_list_0 .sortable2 > .btn:nth-child(1)").click()
        # Click on "Add" in the modal
        self.utils.wait_element_clickable((By.CSS_SELECTOR, ".in > .modal-dialog .button-add")).click()
        # Click on "1.03 Institution name" field
        self.driver.find_element(By.CSS_SELECTOR, "#field_selector_list_0 .sortable2 > .btn:nth-child(1)").click()
        # Click on "Add" in the modal
        self.utils.wait_element_clickable((By.CSS_SELECTOR, ".in > .modal-dialog .button-add")).click()
        # Section 1
        # Click on "1.02 Name" field
        self.driver.find_element(By.CSS_SELECTOR, "#field_selector_list_1 > .col-xs-6 .btn:nth-child(1)").click()
        # Click on "Add" in the modal
        self.utils.wait_element_clickable((By.CSS_SELECTOR, ".in > .modal-dialog .button-add")).click()

        # Click on "1.03 Institution name" field
        self.driver.find_element(By.CSS_SELECTOR, "#field_selector_list_1 .sortable2 > .btn:nth-child(1)").click()
        # Click on "Add" in the modal
        self.utils.wait_element_clickable((By.CSS_SELECTOR, ".in > .modal-dialog .button-add")).click()
        # Click on "Save"
        self.driver.find_element(By.XPATH, "//div[@id='list-view']/div[2]/div[2]/form/button").click()

        # Click on "Card View" tab
        self.driver.find_element(By.LINK_TEXT, "Card View").click()
        # Section 0
        # Click on "1.02 Name" field
        self.driver.find_element(By.CSS_SELECTOR, "#field_selector_card_0 .sortable2 > .btn:nth-child(1)").click()
        # Click on "Add" in the modal
        self.utils.wait_element_clickable((By.CSS_SELECTOR, ".in > .modal-dialog .button-add")).click()
        # Click on "1.03 Institution name" field
        self.driver.find_element(By.CSS_SELECTOR, "#field_selector_card_0 .sortable2 > .btn:nth-child(1)").click()
        # Click on "Add" in the modal
        self.utils.wait_element_clickable((By.CSS_SELECTOR, ".in > .modal-dialog .button-add")).click()

        # Section 1
        # Click on "1.02 Name" field
        self.driver.find_element(By.CSS_SELECTOR, "#field_selector_card_1 > .col-xs-6 .btn:nth-child(1)").click()
        # Click on "Add" in the modal
        self.utils.wait_element_clickable((By.CSS_SELECTOR, ".in > .modal-dialog .button-add")).click()
        # Click on "1.03 Institution name" field
        self.driver.find_element(By.CSS_SELECTOR, "#field_selector_card_1 .sortable2 > .btn:nth-child(1)").click()
        # Click on "Add" in the modal
        self.utils.wait_element_clickable((By.CSS_SELECTOR, ".in > .modal-dialog .button-add")).click()

        # Section 2
        element_to_scroll = self.driver.find_element(
            By.CSS_SELECTOR, "#field_selector_card_2 > .col-xs-6 .btn:nth-child(1)")
        self.driver.execute_script("arguments[0].scrollIntoView();", element_to_scroll)
        # Click on "1.02 Name" field
        self.driver.find_element(By.CSS_SELECTOR, "#field_selector_card_2 > .col-xs-6 .btn:nth-child(1)").click()
        # Click on "Add" in the modal
        self.utils.wait_element_clickable((By.CSS_SELECTOR, ".in > .modal-dialog .button-add")).click()
        # Click on "1.03 Institution name" field
        self.driver.find_element(By.CSS_SELECTOR, "#field_selector_card_2 .sortable2 > .btn:nth-child(1)").click()
        # Click on "Add" in the modal
        self.utils.wait_element_clickable((By.CSS_SELECTOR, ".in > .modal-dialog .button-add")).click()
        # Click on "Save"
        self.driver.find_element(By.XPATH, "//div[@id='card-view']/div[2]/div[2]/form/button").click()

        # Verify that all fields were selected

        # Home
        self.driver.find_element(By.ID, "home").click()

        # Click "Admin panel"
        self.driver.find_element(By.ID, "admin").click()

        # Community fields
        self.driver.find_element(By.XPATH, "//strong[contains(.,'Community fieldss')]").click()

        count = len(self.driver.find_elements_by_xpath("//table[@id='result_list']/tbody/tr"))

        assert count == 12

        # Switch back to landing page
        self.driver.get(self.base_url)

    def table_view(self):
        """
        This method will test the "Table View" view.
        The expected behavior is as follows:
        - Goes to the landing page.
        - Opens the Test community.
        - Opens the left-most questionnaire since it's the one that the fingerprints are using.
        - Clicks on the table icon to make sure that the current view is the table view
        - Verifies if the "Name" and "Institution Name" are currently headers of the displayed table
        - Downloads all the databases
        """
        # Go to the main page
        self.driver.get(self.base_url)

        # Open the TEST community
        self.utils.open_community()

        # Click on the "Table" icon
        self.driver.find_element(By.CSS_SELECTOR, ".fa-table").click()

        # Verify that the expected fields are listed
        name_field = self.driver.find_element(By.XPATH, "//th[contains(.,'Name')]")
        assert name_field.is_displayed()
        institution_name_field = self.driver.find_element(By.XPATH, "//th[contains(.,'Institution name')]")
        assert institution_name_field.is_displayed()

        # Verify that the checkbox is working
        # self.driver.find_element(By.XPATH, "//tbody[@id='table_content']/tr/td[5]/input")

        # Try to download all databases
        self.download_all_databases(valid=True)

    def list_view(self):
        """
        This method will test the "List View" view.
        The expected behavior is as follows:
        - Goes to the landing page.
        - Opens the Test community.
        - Opens the left-most questionnaire since it's the one that the fingerprints are using.
        - Clicks on the list icon to make sure that the current view is the list view
        - Verifies if the "Name" and "Institution Name" for selected questionnaire's community fingerprints are listed
        - Downloads all the databases
        """
        # Go to the main page
        self.driver.get(self.base_url)

        # Open the TEST community
        self.utils.open_community()

        # Click on the "List" icon
        self.driver.find_element(By.CSS_SELECTOR, ".fa-list").click()

        # Verify that the expected fields are listed
        assert data.fingerprint_name in self.driver.page_source
        assert data.fingerprint_institution in self.driver.page_source

        # Try to download all databases
        self.download_all_databases(valid=True)

    def card_view(self):
        """
        This method will test the "Card View" view.
        The expected behavior is as follows:
        - Goes to the landing page.
        - Opens the Test community.
        - Opens the left-most questionnaire since it's the one that the fingerprints are using.
        - Clicks on the card icon to make sure that the current view is the card view
        - Verifies if the "Name" and "Institution Name" for selected questionnaire's community fingerprints are listed
        - Downloads all the databases
        """
        # Go to the main page
        self.driver.get(self.base_url)

        # Open the TEST community
        self.utils.open_community()

        # Click on the "Card" icon
        self.driver.find_element(By.CSS_SELECTOR, ".fa-th-large").click()

        # Verify that the expected fields are listed
        assert data.fingerprint_name in self.driver.page_source
        assert data.fingerprint_institution in self.driver.page_source

        # Try to download all databases
        self.download_all_databases(valid=True)

    def download_all_databases(self, valid=False):
        """
        This method will test the "Export all databases" feature by downloading all fingerprints.
        The expected behavior is as follows:
        - Goes to the landing page.
        - Opens the Test community.
        - Selects "Export" -> "All databases"
        - Confirms the download and waits for two seconds.
        - Clicks "here" in the intermediary page and waits for two seconds
        - Clicks "Download" when the progress of the job queue hits 100%
        - Waits for 5 seconds so the download has time to finish.
        - Verifies if the files were downloaded by scanning the download directory for files that end with
         ".csv" , which is the file type of the downloaded databases.
        - Deletes the downloaded files.

        Note:
            The download directory is specified in the parent class.

        Args:
            valid: Whether the test should pass or not.
        """
        # Go to the main page
        self.driver.get(self.base_url)

        # Open the TEST community
        self.utils.open_community()

        # Export all databases
        self.driver.find_element(By.ID, "dropdownMenu2").click()
        self.driver.find_element(By.LINK_TEXT, "All databases").click()
        self.driver.find_element(By.XPATH, "// button[contains(., 'OK')]").click()

        self.utils.check_job_output_file(
            lambda f: "EMIF_Catalogue" in f and "DBs" in f and f.endswith('.csv'),
            self.download_path,
            valid,
        )
