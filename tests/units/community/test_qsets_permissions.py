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

import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException

from utils.testcases import MontraTestCase
from utils.data import MontraTestData as data


class QSetsPermissionsTestCase(MontraTestCase):

    def test_qsets_permissions(self):

        self.verify_user1_denied_access()

        self.add_user1_to_default_group()

        self.set_default_qsets_permissions()

        self.verify_user1_default_access()

        self.modify_q_sets_permissions()

        self.verify_user1_modified_access()

        self.modify_q_sets_permissions()  # to set default qset permissions

    def verify_user1_denied_access(self):

        user1 = data.users["user1"]

        # Login as user1
        self.utils.login(user1["username"], user1["password"])

        self.utils.open_community()

        count = self.utils.get_number_of_fingerprints()

        current_fingerprint_acronym = data.fingerprint_acronym + str(count)

        # Open fingerprint
        self.driver.find_element(By.CSS_SELECTOR, "a[data-acronym={}]".format(current_fingerprint_acronym)).click()

        start_time = time.time()
        while True:

            if "You don't have permission to access this questionnaire section" in self.driver.page_source:
                break

            assert time.time() - start_time < 10, "Denied permission msg did not appear after 10 seconds"

        self.utils.logout()

    def add_user1_to_default_group(self):

        user2 = data.users["user2"]

        # Login as user2
        self.utils.login(user2["username"], user2["password"])

        # Open community
        self.driver.find_element(By.LINK_TEXT, "OPEN").click()

        # Manage tab
        manage_menu_button = self.driver.find_element(By.ID, "mancomm")
        manage_menu_button.click()

        # Open groups page
        manage_menu_button.find_element(By.XPATH, '../../ul//a[text()[contains(., "Groups")]]').click()

        # Add user1 to default group
        self.utils.click_table_item(
            "groups_and_users",
            "default",
            'td[text()="user1@emiftest.pt"]/..',
            'input',
        )

        # Save
        self.driver.find_element(By.CSS_SELECTOR, ".user-groups-plugins-container .btn-success").click()

        # Wait for modal to appear
        element = self.utils.wait_element_clickable((By.CSS_SELECTOR, ".btn-primary"))

        # Click on "Ok"
        element.click()

        # Wait for modal to disappear
        self.utils.wait_element_invisible((By.CSS_SELECTOR, ".btn-primary"))

    def set_default_qsets_permissions(self):

        # Manage tab
        manage_menu_button = self.driver.find_element(By.ID, "mancomm")
        manage_menu_button.click()

        # Open Question Sets page
        manage_menu_button.find_element(By.XPATH, '../../ul//a[text()[contains(., "Question Sets")]]').click()

        # Give all qsets read permissions to default group
        self.driver.find_element(By.XPATH, '//b[text()="default"]/../..//label[contains(@for, "read_all")]').click()

        # Give all qsets read and write permissions to editors group
        self.driver.find_element(By.XPATH, '//b[text()="editors"]/../..//label[contains(@for, "write_all")]').click()

        # Save
        self.driver.find_element(By.CSS_SELECTOR, ".btn-success").click()

        # Wait for modal to appear
        element = self.utils.wait_element_clickable((By.CSS_SELECTOR, ".btn-primary"))

        # Click on "Ok"
        element.click()

        # Wait for modal to disappear
        self.utils.wait_element_invisible((By.CSS_SELECTOR, ".btn-primary"))

        self.utils.logout()

    def verify_user1_default_access(self):

        user1 = data.users["user1"]

        # Login as user1
        self.utils.login(user1["username"], user1["password"])

        self.utils.open_community()

        count = self.utils.get_number_of_fingerprints()

        current_fingerprint_acronym = data.fingerprint_acronym + str(count)

        # Verify user1 has access to all question sets
        self.utils.verfiy_access_to_all_qsets(current_fingerprint_acronym)

        self.utils.logout()

    def modify_q_sets_permissions(self):

        user2 = data.users["user2"]

        # Login as user2
        self.utils.login(user2["username"], user2["password"])

        # Open community
        self.driver.find_element(By.LINK_TEXT, "OPEN").click()

        # Manage tab
        manage_menu_button = self.driver.find_element(By.ID, "mancomm")
        manage_menu_button.click()

        # Open Question Sets page
        manage_menu_button.find_element(By.XPATH, '../../ul//a[text()[contains(., "Question Sets")]]').click()

        # Read permissions from qset 4 Technical Details
        self.utils.click_table_item(
            "groups_qsets",
            "Technical Details",
            'b[text()="default"]/../..',
            'label[@data-original-title="Read"]',
        )

        # Read permissions from qset 6 Publications
        self.utils.click_table_item(
            "groups_qsets",
            "Publications",
            'b[text()="default"]/../..',
            'label[@data-original-title="Read"]',
        )

        # Write permissions to qset 5 Data Governance And Ethics
        self.utils.click_table_item(
            "groups_qsets",
            "Data Governance and Ethics",
            'b[text()="default"]/../..',
            'label[@data-original-title="Write"]',
        )

        # Save
        self.driver.find_element(By.CSS_SELECTOR, ".btn-success").click()

        # Wait for modal to appear
        element = self.utils.wait_element_clickable((By.CSS_SELECTOR, ".btn-primary"))

        # Click on "Ok"
        element.click()

        # Wait for modal to disappear
        self.utils.wait_element_invisible((By.CSS_SELECTOR, ".btn-primary"))

        self.utils.logout()

    def verify_user1_modified_access(self):

        user1 = data.users["user1"]

        # Login as user1
        self.utils.login(user1["username"], user1["password"])

        self.utils.open_community()

        count = self.utils.get_number_of_fingerprints()

        current_fingerprint_acronym = data.fingerprint_acronym + str(count)

        # Open fingerprint
        self.driver.find_element(By.CSS_SELECTOR, "a[data-acronym={}]".format(current_fingerprint_acronym)).click()

        # Wait for contents to appear (implicit wait)
        self.driver.find_element(By.ID, "question_1.01")

        # Verify contents of question_set 1
        assert current_fingerprint_acronym in self.driver.page_source
        assert data.fingerprint_name in self.driver.page_source
        assert "test question_1.07.04" in self.driver.page_source

        # Click on question_set 2, wait, and verify contents
        self.driver.find_element(By.ID, "counter1_2").click()
        self.driver.find_element(By.ID, "question_2.01")
        assert "test question_2.05_more1" in self.driver.page_source
        assert "Aveiro" in self.driver.page_source
        assert "Portugal" in self.driver.page_source

        # Verify question_set 4 is not clickable
        with self.assertRaises(ElementClickInterceptedException):
            self.driver.find_element(By.ID, "counter1_4").click()

        # Verify question_set 6 is not clickable
        with self.assertRaises(ElementClickInterceptedException):
            self.driver.find_element(By.ID, "counter1_6").click()

        # Click on question_set 5, wait, and verify contents
        self.driver.find_element(By.ID, "counter1_5").click()
        self.driver.find_element(By.ID, "question_5.03")
        assert "test question_5.05" in self.driver.page_source
        assert "test question_5.11" in self.driver.page_source

        # Click on question_set 1, wait, and verify contents
        self.driver.find_element(By.ID, "counter1_1").click()
        self.driver.find_element(By.ID, "question_1.01")
        assert data.fingerprint_name in self.driver.page_source
        assert "test question_1.07.04" in self.driver.page_source

        # Edit qset 5
        self.driver.find_element(By.CSS_SELECTOR, "li:nth-child(4) .fa-pen-square").click()
        self.driver.find_element(By.ID, "question_5.03").clear()
        self.driver.find_element(By.ID, "question_5.03").send_keys("question_5.03_edited")
        self.driver.find_element(By.NAME, "submit").click()
        self.driver.find_element(By.ID, "cancel_link").click()

        self.driver.find_element(By.ID, "question_5.03")
        assert "test question_5.03" not in self.driver.page_source
        assert "question_5.03_edited" in self.driver.page_source

        # Edit again to default value
        self.driver.find_element(By.CSS_SELECTOR, "li:nth-child(4) .fa-pen-square").click()
        self.driver.find_element(By.ID, "question_5.03").clear()
        self.driver.find_element(By.ID, "question_5.03").send_keys("test question_5.03")
        self.driver.find_element(By.NAME, "submit").click()
        self.driver.find_element(By.ID, "cancel_link").click()

        self.driver.find_element(By.ID, "question_5.03")
        assert "test question_5.03" in self.driver.page_source
        assert "question_5.03_edited" not in self.driver.page_source

        self.utils.logout()
