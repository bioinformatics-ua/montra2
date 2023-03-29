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


class FingerprintDeleteTestCase(MontraTestCase):

    def test_fingerprint_delete(self):

        user2 = data.users["user2"]

        # Login as user2
        self.utils.login(user2["username"], user2["password"])

        self.utils.open_community()

        count = self.utils.get_number_of_fingerprints()

        current_fingerprint_acronym = data.fingerprint_acronym + str(count)

        assert current_fingerprint_acronym in self.driver.page_source

        # Open fingerprint to delete
        self.driver.find_element(By.CSS_SELECTOR, "a[data-acronym={}]".format(current_fingerprint_acronym)).click()

        # Open modal Manage/Delete
        self.driver.find_element(By.ID, "managetoolbar").click()
        self.driver.find_element(By.ID, "delete_list_toolbar").click()

        # Click Delete
        element = self.utils.wait_element_clickable((By.ID, "delete_fingerprint"))
        element.click()

        # Wait for modal to disappear
        self.utils.wait_element_invisible((By.ID, "delete_fingerprint"))

        # Home
        self.driver.find_element(By.ID, "home").click()

        # Open community
        self.utils.open_community()

        # Verify fingerprint does not exist
        assert current_fingerprint_acronym not in self.driver.page_source
