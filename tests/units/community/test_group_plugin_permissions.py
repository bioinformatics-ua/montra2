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


class GroupPluginPermissionsTestCase(MontraTestCase):

    def test_group_plugin_permissions(self):

        self.add_plugin_to_comm()

        self.verify_user1_can_not_access()

        self.add_user1_to_plugin_group()

        self.verify_user1_can_access()

    def add_plugin_to_comm(self):

        user2 = data.users["user2"]

        # Login as user2
        self.utils.login(user2["username"], user2["password"])

        # Open community
        self.driver.find_element(By.LINK_TEXT, "OPEN").click()

        assert data.plugin_name not in self.driver.page_source

        # Manage tab
        manage_menu_button = self.driver.find_element(By.ID, "mancomm")
        manage_menu_button.click()

        # Open components page
        manage_menu_button.find_element(By.XPATH, '../../ul//a[text()[contains(., "Components")]]').click()

        # Click on the plugin
        self.driver.find_element(By.CSS_SELECTOR, ".btn-blue:nth-child(1)").click()

        # Save
        self.driver.find_element(By.CSS_SELECTOR, ".panel-body:nth-child(4) > form > .btn").click()

        # Verify user2 can access plugin
        self.driver.find_element(By.ID, "home").click()
        self.driver.find_element(By.LINK_TEXT, "OPEN").click()
        assert data.plugin_name in self.driver.page_source

        self.utils.logout()

    def verify_user1_can_not_access(self):

        user1 = data.users["user1"]

        # Login as user1
        self.utils.login(user1["username"], user1["password"])

        # Open community
        self.driver.find_element(By.LINK_TEXT, "OPEN").click()

        assert data.plugin_name not in self.driver.page_source

        self.utils.logout()

    def add_user1_to_plugin_group(self):

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

        # Add test_plugin to test_group
        self.utils.click_table_item(
            "groups_plugins",
            "test_plugin",
            'b[text()="test_group"]/../..',
            "input",
        )

        # Save
        self.driver.find_element(By.CSS_SELECTOR, ".panel:nth-child(1) .btn-toolbar > .btn-success").click()

        # Wait for modal to appear
        element = self.utils.wait_element_clickable((By.CSS_SELECTOR, ".btn-primary"))

        # Click on "Ok"
        element.click()

        # Wait for modal to disappear
        self.utils.wait_element_invisible((By.CSS_SELECTOR, ".btn-primary"))

        # Add user1 to test_group
        self.utils.click_table_item(
            "groups_and_users",
            "test_group",
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

        assert data.plugin_name in self.driver.page_source
