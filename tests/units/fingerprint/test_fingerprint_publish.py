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


class FingerprintPublishTestCase(MontraTestCase):

    def test_fingerprint_publish(self):

        user2 = data.users["user2"]

        # Login as user2
        self.utils.login(user2["username"], user2["password"])

        self.utils.open_community()

        assert "DRAFT" in self.driver.page_source

        count = self.utils.get_number_of_fingerprints()

        current_fingerprint_acronym = data.fingerprint_acronym + str(count)

        assert current_fingerprint_acronym in self.driver.page_source

        assert "DRAFT" in self.driver.page_source

        # Open fingerprint
        self.driver.find_element(By.CSS_SELECTOR, "a[data-acronym={}]".format(current_fingerprint_acronym)).click()

        # Uncheck draft checkbok to request to make this fingerprint public
        self.driver.find_element(By.ID, "managetoolbar").click()
        self.driver.find_element(By.ID, "edit_list_toolbar").click()
        self.driver.find_element(By.CSS_SELECTOR, ".checkbox > label").click()

        # Go to manage menu
        manage_button_menu = self.driver.find_element(By.ID, "mancomm")
        manage_button_menu.click()

        # Draft menu
        manage_button_menu.find_element(By.XPATH, '../../ul//a[text()[contains(., "Drafts")]]').click()

        # Validate draft
        self.driver.find_element(By.CSS_SELECTOR, ".btn-link").click()

        # Database catalogue
        databases_button_menu = self.driver.find_element(By.ID, "databases")
        databases_button_menu.click()

        # Databases
        databases_button_menu.find_element(By.XPATH, '../../ul//a[text()[contains(., "Databases")]]').click()

        self.driver.refresh()

        assert current_fingerprint_acronym in self.driver.page_source

        assert "DRAFT" not in self.driver.page_source
