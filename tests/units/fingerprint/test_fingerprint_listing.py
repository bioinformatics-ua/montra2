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


class FingerprintListingTestCase(MontraTestCase):
    """
    This test will verify that the fingerprint listing feature is working properly.
    Namely, it will test the following toolbar features:

    1- Selection of fingerprints

    2- Comparison between fingerprints

    3- Export selected fingerprints

    4- Export all databases
    """

    def test_fingerprint_listing(self):

        user2 = data.users["user2"]
        user1 = data.users["user1"]

        # Login with user2, who has permissions
        self.utils.login(user2["username"], user2["password"])

        # Verify that user 2 is logged in
        assert user2["first_name"] in self.driver.page_source
        assert user2["last_name"] in self.driver.page_source

        # Compare two fingerprints
        self.compare_two_fingerprints()

        # Try to download both fingerprints.
        # It should work since the user is a superuser
        self.download_two_fingerprints(allowed=True)

        # Try to download all databases.
        # It should work since the user is a superuser
        self.download_all_databases(allowed=True)

        self.download_selected_multimontra(allowed=True)

        self.utils.logout()

        # Verify that user 2 is logged out
        assert user2["first_name"] not in self.driver.page_source
        assert user2["last_name"] not in self.driver.page_source

        # Login with user1, who does not have permissions
        self.utils.login(user1["username"], user1["password"])

        # Verify that user 1 is logged in
        assert user1["first_name"] in self.driver.page_source
        assert user1["last_name"] in self.driver.page_source

        # Try to download both fingerprints.
        # It should work since the user1 has permissions for exporting.
        self.download_two_fingerprints(allowed=True)

        # Try to download all databases.
        # It should work since the user1 has permissions for exporting.
        # This setting is set, while inside a community, in Manage-> Allow Users to Export Databases.
        self.download_all_databases(allowed=True)

        self.download_selected_multimontra(allowed=False)

    def compare_two_fingerprints(self):
        """
        This method will test the "Compare" fingerprints functionality.
        The expected behaviour is as follows:
        - Goes to the landing page.
        - Opens the Test community.
        - Select two fingerprints and verifies that the checkbox is working.
        - Select "Compare" and goes to the "Compare" page
        - Clicks on a tab of the comparison table
        """
        # Go to the main page
        self.driver.get(self.base_url)

        # Open the TEST community
        self.utils.open_community()

        # Select two fingerprints
        checkbox_one = self.driver.find_element(By.XPATH, "//tbody[@id='table_content']/tr/td[3]/input")
        checkbox_one.click()
        assert checkbox_one.is_selected()

        checkbox_two = self.driver.find_element(By.XPATH, "//tbody[@id='table_content']/tr[2]/td[3]/input")
        checkbox_two.click()
        assert checkbox_two.is_selected()

        # Click on "Compare"
        self.driver.find_element(By.ID, "dropdownMenu1").click()
        # Click on "Databases"
        self.driver.find_element(By.ID, "comparabtn").click()
        # Click on "Close"
        self.driver.find_element(By.XPATH, "//button[contains(.,'Close')]").click()
        # Click on "Database General Information"
        self.driver.find_element(By.XPATH, "//div[@id='sm1']/div")

    def download_two_fingerprints(self, allowed=False):
        """
        This method will test the "Export selected fingerprints" feature by downloading two fingerprints.
        The expected behavior is as follows:
        - Goes to the landing page.
        - Opens the Test community.
        - Select two fingerprints and verifies that the checkbox is working.
        - Selects "Export" -> "Selected Fingerprints".
        - Waits for 5 seconds so the download has time to finish.
        - Confirms the download and verifies if the files were downloaded by scanning the download directory for
        files that end with ".csv" , which is the file type of the downloaded fingerprints.
        - Deletes the downloaded files.

        Note:
            The download directory is specified in the parent class.

        Args:
            allowed: Whether the user has permissions to perform the opration
        """
        # Go to the main page
        self.driver.get(self.base_url)

        # Open the TEST community
        self.utils.open_community()

        # Select two fingerprints
        checkbox_one = self.driver.find_element(By.XPATH, "//tbody[@id='table_content']/tr/td[3]/input")
        checkbox_one.click()
        assert checkbox_one.is_selected()

        checkbox_two = self.driver.find_element(By.XPATH, "//tbody[@id='table_content']/tr[2]/td[3]/input")
        checkbox_two.click()
        assert checkbox_two.is_selected()

        # Part 3
        # Export selected fingerprints
        self.driver.find_element(By.ID, "dropdownMenu2").click()
        self.driver.find_element(By.LINK_TEXT, "Selected databases").click()

        # Download the selected fingerprints
        self.driver.find_element(By.XPATH, "//button[contains(.,'Yes')]").click()
        time.sleep(5)

        self.utils.check_job_output_file(
            lambda f: "EMIF_Catalogue" in f and "SelectedDBs" in f and f.endswith('.csv'),
            self.download_path,
            allowed,
        )

    def download_all_databases(self, allowed=False):
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
            allowed: Whether the user has permissions to perform the opration
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
            allowed,
        )

    def download_selected_multimontra(self, allowed):
        """
        This method will test the "Export selected fingerprints (Multimontra)" feature by downloading two fingerprints.
        The expected behavior is as follows:
        - Goes to the landing page.
        - Opens the Test community.
        - Select two fingerprints and verifies that the checkbox is working.
        - Selects "Export" -> "Selected Fingerprints (Multimontra)".
        - Waits for 5 seconds so the download has time to finish.
        - Confirms the download and verifies if the files were downloaded by scanning the download directory for
        files that end with ".multimontra" , which is the file type of the downloaded fingerprints.
        - Deletes the downloaded files.

        Note:
            The download directory is specified in the parent class.

        Args:
            allowed: Whether the test should pass or not.
        """

        # Go to the main page
        self.driver.get(self.base_url)

        # Open the TEST community
        self.utils.open_community()

        # Select two fingerprints
        checkbox_one = self.driver.find_element(By.XPATH, "//tbody[@id='table_content']/tr/td[3]/input")
        checkbox_one.click()
        assert checkbox_one.is_selected()

        checkbox_two = self.driver.find_element(By.XPATH, "//tbody[@id='table_content']/tr[2]/td[3]/input")
        checkbox_two.click()
        assert checkbox_two.is_selected()

        # Part 3
        # Export selected fingerprints in multimontra format
        self.driver.find_element(By.ID, "dropdownMenu2").click()
        if not allowed:
            assert "Selected databases (Multimontra)" not in self.driver.page_source
            return

        self.driver.find_element(By.LINK_TEXT, "Selected databases (Multimontra)").click()

        # Download the selected fingerprints
        self.driver.find_element(By.XPATH, "//button[contains(.,'Yes')]").click()
        time.sleep(5)

        self.utils.check_job_output_file(
            lambda f: "SelectedDBs" in f and f.endswith('.multimontra'),
            self.download_path,
            True,
        )
