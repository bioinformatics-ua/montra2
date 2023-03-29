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


class GroupAPITestCase(MontraTestCase):

    def test_group_api(self):

        self.verify_user1_can_not_access()

        self.add_user1_to_api_group()

        self.verify_user1_can_access()

    def verify_user1_can_not_access(self):

        user1 = data.users["user1"]

        # Login as user1
        self.utils.login(user1["username"], user1["password"])

        # Open community
        self.driver.find_element(By.LINK_TEXT, "OPEN").click()

        assert "API Info" not in self.driver.page_source

        self.utils.logout()

    def add_user1_to_api_group(self):

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

        # Add user1 to api group
        self.utils.click_table_item(
            "groups_and_users",
            "API",
            'td[text()="user1@emiftest.pt"]/..',
            "input",
        )

        # Save
        self.driver.find_element(By.CSS_SELECTOR, ".user-groups-plugins-container .btn-success").click()

        # Wait for modal to appear
        element = self.utils.wait_element_clickable((By.CSS_SELECTOR, ".btn-primary"))

        # Click on "Ok"
        element.click()

        # Wait for modal to disappear
        self.utils.wait_element_invisible((By.CSS_SELECTOR, ".btn-primary"))

        self.utils.logout()

    def verify_user1_can_access(self):

        user1 = data.users["user1"]

        # Login as user1
        self.utils.login(user1["username"], user1["password"])

        # Open community
        self.driver.find_element(By.LINK_TEXT, "OPEN").click()

        assert "API Info" in self.driver.page_source

        self.driver.find_element(By.ID, "apiinfo").click()

        assert 'API Info Details' in self.driver.page_source
