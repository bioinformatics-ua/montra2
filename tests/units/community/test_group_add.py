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


class GroupAddTestCase(MontraTestCase):

    def test_group_add(self):

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

        assert data.group_name not in self.driver.page_source

        # Add group btn
        self.driver.find_element(By.XPATH, "//button[@onclick=\'addGroup();\']").click()

        # Insert group name
        self.driver.find_element(By.ID, "gname").click()
        self.driver.find_element(By.ID, "gname").send_keys(data.group_name)

        # Add btn
        self.driver.find_element(By.CSS_SELECTOR, ".modal-footer > .btn-success").click()

        # # Confirm group was inserted

        # Home
        self.driver.get(self.base_url)

        # Open community
        self.driver.find_element(By.LINK_TEXT, "OPEN").click()

        # Manage tab
        manage_menu_button = self.driver.find_element(By.ID, "mancomm")
        manage_menu_button.click()

        # Open groups page
        manage_menu_button.find_element(By.XPATH, '../../ul//a[text()[contains(., "Groups")]]').click()

        assert data.group_name in self.driver.page_source
