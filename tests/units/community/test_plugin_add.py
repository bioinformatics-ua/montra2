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
from selenium.webdriver.support.ui import Select

from utils.testcases import MontraTestCase
from utils.data import MontraTestData as data


class PluginAddTestCase(MontraTestCase):

    def test_plugin_add(self):

        user2 = data.users["user2"]

        # Login as user2
        self.utils.login(user2["username"], user2["password"])

        # Developers tab
        self.driver.find_element(By.ID, "developer").click()

        assert data.plugin_name not in self.driver.page_source

        # Add Plugin btn
        self.driver.find_element(By.ID, "developer_add").click()

        # Fill plugin name
        self.driver.find_element(By.ID, "id-name").click()
        self.driver.find_element(By.ID, "id-name").send_keys(data.plugin_name)

        # Choose "Clickable link" type
        self.driver.find_element(By.ID, "id-type").click()

        dropdown = Select(self.driver.find_element(By.ID, "id-type"))
        dropdown.select_by_visible_text("Third party full-fledged applications")

        # Save plugin btn
        self.driver.find_element(By.ID, "save-plugin").click()

        # Add version btn
        self.driver.find_element(By.LINK_TEXT, "Add version").click()

        # Fill path
        self.driver.find_element(By.ID, "id-path").click()
        self.driver.find_element(By.ID, "id-path").send_keys("https://www.google.com/")

        # Save btn
        self.driver.find_element(By.ID, "save-version").click()

        # Submit btn
        self.driver.find_element(By.ID, "submit-version").click()

        assert "This version is approved, any changes will undo this status." not in self.driver.page_source

        # Wait for modal to appear
        element = self.utils.wait_element_clickable((By.XPATH, "//button[contains(.,\'OK\')]"))

        # Click on "Ok"
        element.click()

        # Wait for modal to disappear
        self.utils.wait_element_invisible((By.XPATH, "//button[contains(.,\'OK\')]"))

        assert "This version is approved, any changes will undo this status." in self.driver.page_source

        # Developers tab
        self.driver.find_element(By.ID, "developer").click()

        assert data.plugin_name in self.driver.page_source
