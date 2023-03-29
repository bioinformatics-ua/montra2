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

from utils.testcases import MontraTestCase
from utils.data import MontraTestData as data


class FingerprintShareOwnershipTestCase(MontraTestCase):
    """
    Test if removing a shared ownership removes the access to the fingerprint in question.
    Works on both public and draft fingerprints.
    Main steps:

    1- User2 (owner) shares ownership with user1

    2- User1 accepts ownership

    3- User2 removes user1 ownership

    4- Verify user1 is not owner or Verify user1 can not access draft
    """

    is_draft = False

    def test_fingerprint_share_ownership(self):

        user2 = data.users["user2"]
        user1 = data.users["user1"]

        # # # User2 (owner) shares ownership with user1

        # Login as user2
        self.utils.login(user2["username"], user2["password"])

        self.utils.open_community()

        count = self.utils.get_number_of_fingerprints()

        current_fingerprint_acronym = data.fingerprint_acronym + str(count)

        # Open fingerprint
        self.driver.find_element(By.CSS_SELECTOR, "a[data-acronym={}]".format(current_fingerprint_acronym)).click()

        # Manage/Members with ownership
        self.driver.find_element(By.ID, "managetoolbar").click()
        self.driver.find_element(By.ID, "editpermissions").click()

        # Wait for modal to appear
        element = self.utils.wait_element_clickable((By.LINK_TEXT, "Cancel"))

        # Verify user1 is not owner yet
        assert user1["first_name"] not in self.driver.page_source
        assert user1["last_name"] not in self.driver.page_source

        # Click on "Cancel"
        element.click()

        self.driver.refresh()

        # Manage/Share with other user
        self.driver.find_element(By.ID, "managetoolbar").click()
        self.driver.find_element(By.ID, "share_list_toolbar").click()

        # Insert user1 email and share
        self.driver.find_element(By.ID, "share_email").send_keys(user1["email"])
        self.driver.find_element(By.CSS_SELECTOR, ".control-label").click()

        valid_email_msg = "Email is valid and belongs to {} {}.".format(
            user1["first_name"], user1["last_name"])

        start_time = time.time()
        while True:

            if valid_email_msg in self.driver.page_source:
                break

            assert time.time() - start_time < 10, "Valid email msd did not appear after 10 seconds"

        self.driver.find_element(By.CSS_SELECTOR, ".sharedb2").click()
        self.driver.find_element(By.LINK_TEXT, "Cancel").click()

        self.utils.logout()

        # # # User1 accepts ownership

        # Login as user1
        self.utils.login(user1["username"], user1["password"])

        # Open notifications
        self.driver.find_element(By.ID, "notifications").click()

        # Click on notification and stop loading because of email not auth error
        self.driver.find_element(By.CSS_SELECTOR, "#user_notifications strong").click()
        time.sleep(2)
        self.driver.execute_script("window.stop();")

        # Open landing page
        self.driver.get(self.base_url)

        self.utils.open_community()

        # Open fingerprint
        self.driver.find_element(By.CSS_SELECTOR, "a[data-acronym={}]".format(current_fingerprint_acronym)).click()

        # Verify user1 is owner
        assert "managetoolbar" in self.driver.page_source

        # Manage/Members with ownership
        self.driver.find_element(By.ID, "managetoolbar").click()
        self.driver.find_element(By.ID, "editpermissions").click()

        # Wait for modal to appear
        element = self.utils.wait_element_clickable((By.LINK_TEXT, "Cancel"))

        # Verify user1 is owner
        assert user1["first_name"] in self.driver.page_source
        assert user1["last_name"] in self.driver.page_source

        # Click on "Cancel"
        element.click()

        self.driver.refresh()

        # Click on "Home"
        self.driver.find_element(By.ID, "home").click()

        # Open notifications
        self.driver.find_element(By.ID, "notifications").click()

        notification_str = "{} has been shared with you, please click here to".format(current_fingerprint_acronym)

        assert notification_str in self.driver.page_source

        # Remove notification
        self.driver.find_element(By.CSS_SELECTOR, "#user_notifications .notification_delete path").click()

        self.driver.refresh()

        assert notification_str not in self.driver.page_source, "Notification was not removed."

        self.utils.logout()

        # # # User2 removes user1 ownership

        # Login as user2
        self.utils.login(user2["username"], user2["password"])

        self.utils.open_community()

        # Open fingerprint
        self.driver.find_element(By.CSS_SELECTOR, "a[data-acronym={}]".format(current_fingerprint_acronym)).click()

        # Manage/Members with ownership
        self.driver.find_element(By.ID, "managetoolbar").click()
        self.driver.find_element(By.ID, "editpermissions").click()

        # Wait for modal to appear
        element = self.utils.wait_element_clickable((By.CSS_SELECTOR, ".btn-sm:nth-child(2)"))

        # Verify user1 is owner
        assert user1["first_name"] in self.driver.page_source
        assert user1["last_name"] in self.driver.page_source

        # Click on "Remove" user1 ownership
        element.click()

        # Wait for other confirmation modal to appear
        element = self.utils.wait_element_clickable((By.CSS_SELECTOR, ".btn-primary"))

        # Click on "Confirm"
        element.click()

        # Exit modal
        self.driver.find_element(By.LINK_TEXT, "Cancel").click()

        self.utils.logout()

        # # # Verify user1 is not owner or Verify user1 can not access draft

        # Login as user1
        self.utils.login(user1["username"], user1["password"])

        self.utils.open_community()

        if self.is_draft:
            # Verify user1 can not access draft
            assert "DRAFT" not in self.driver.page_source
            assert 'data-acronym="' + current_fingerprint_acronym not in self.driver.page_source
        else:
            # Open fingerprint
            self.driver.find_element(By.CSS_SELECTOR, "a[data-acronym={}]".format(current_fingerprint_acronym)).click()

            # Verify user1 is not owner
            assert "managetoolbar" not in self.driver.page_source

        self.utils.logout()
