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


class FingerprintPrivateLinkTestCase(MontraTestCase):

    def test_fingerprint_private_link(self):

        user2 = data.users["user2"]

        # Login as user2
        self.utils.login(user2["username"], user2["password"])

        self.utils.open_community()

        count = self.utils.get_number_of_fingerprints()

        current_fingerprint_acronym = data.fingerprint_acronym + str(count)

        assert current_fingerprint_acronym in self.driver.page_source

        # Open fingerprint
        self.driver.find_element(By.CSS_SELECTOR, "a[data-acronym={}]".format(current_fingerprint_acronym)).click()

        # Manage/Private link
        self.driver.find_element(By.ID, "managetoolbar").click()
        self.driver.find_element(By.ID, "publiclink_toolbar").click()

        # Click create private link
        element = self.utils.wait_element_clickable((By.ID, "createpubliclink"))
        element.click()

        # Open private link
        self.driver.find_element(By.LINK_TEXT, "Private Link").click()

        # Save private link
        private_link = self.driver.current_url

        assert "public" in private_link

        # Enter in private link and verify access is granted
        self.driver.get(private_link)

        # Wait for contents to appear
        self.driver.find_element(By.ID, "question_1.01")

        assert current_fingerprint_acronym in self.driver.page_source
        assert data.fingerprint_name in self.driver.page_source

        # Logout
        self.utils.logout()

        # Enter in private link and verify access is granted to a non-logged in user
        self.driver.get(private_link)
        assert "Anonymous" in self.driver.page_source

        # Wait for contents to appear
        self.driver.find_element(By.ID, "question_1.01")

        # Verify contents of question_set 1
        assert current_fingerprint_acronym in self.driver.page_source
        assert data.fingerprint_name in self.driver.page_source
        assert "test question_1.07.04" in self.driver.page_source

        # Click on question_set 2, wait, and verify contents
        self.driver.find_element(By.CSS_SELECTOR, "#li_qs_2 > a").click()
        self.driver.find_element(By.ID, "question_2.01")
        assert "test question_2.05_more1" in self.driver.page_source
        assert "Aveiro" in self.driver.page_source
        assert "Portugal" in self.driver.page_source

        # Click on question_set 4, wait, and verify contents
        self.driver.find_element(By.CSS_SELECTOR, "#li_qs_4 > a").click()
        self.driver.find_element(By.ID, "question_4.01")
        assert "test question_4.01" in self.driver.page_source
        assert "test question_4.06" in self.driver.page_source

        # Click on question_set 5, wait, and verify contents
        self.driver.find_element(By.ID, "counter1_5").click()
        self.driver.find_element(By.ID, "question_5.03")
        assert "test question_5.05" in self.driver.page_source
        assert "test question_5.11" in self.driver.page_source

        # Click on question_set 6, wait, and verify contents
        self.driver.find_element(By.ID, "counter1_6").click()
        self.driver.find_element(By.ID, "question_601_pubmedid")
        assert "test question_601_pubauthors" in self.driver.page_source
        assert "test question_6.03\ntest question_6.03" in self.driver.page_source

        # Click on question_set 1, wait, and verify contents
        self.driver.find_element(By.ID, "counter1_1").click()
        self.driver.find_element(By.ID, "question_1.01")
        assert data.fingerprint_name in self.driver.page_source
        assert "test question_1.07.04" in self.driver.page_source

        # Login as user2
        self.utils.login(user2["username"], user2["password"])

        self.utils.open_community()

        # Open fingerprint
        self.driver.find_element(By.CSS_SELECTOR, "a[data-acronym={}]".format(current_fingerprint_acronym)).click()

        # Open modal Manage/Private link
        self.driver.find_element(By.ID, "managetoolbar").click()
        self.driver.find_element(By.ID, "publiclink_toolbar").click()

        # Click on Delete private link
        self.utils.wait_element_clickable((By.CSS_SELECTOR, ".btn > img")).click()
        self.utils.wait_element_invisible((By.CSS_SELECTOR, ".btn > img"))

        # Enter in private link and verify access is not granted while logged in
        self.driver.get(private_link)
        assert current_fingerprint_acronym not in self.driver.page_source
        assert data.fingerprint_name not in self.driver.page_source
        assert "404" in self.driver.page_source

        # Logout
        self.utils.logout()

        # Enter in private link and verify access is not granted while logged out
        self.driver.get(private_link)
        assert current_fingerprint_acronym not in self.driver.page_source
        assert data.fingerprint_name not in self.driver.page_source
        assert "404" in self.driver.page_source
