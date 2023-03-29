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


class CommunityAccessControlTestCase(MontraTestCase):

    def test_community_access_control(self):

        user1 = data.users["user1"]

        # Login as user1
        self.utils.login(user1["username"], user1["password"])

        self.utils.open_community()

        # Certify access to community
        assert data.community_name in self.driver.page_source
        assert "sorter-database_name" in self.driver.page_source

        # Save community link
        community_link = self.driver.current_url

        self.utils.logout()

        # Remove user1 from community
        self.utils.comm_user_remove()

        # Login as user1
        self.utils.login(user1["username"], user1["password"])

        # Certify join button
        assert "JOIN" in self.driver.page_source

        self.driver.find_element(By.LINK_TEXT, "JOIN").click()

        # Certify denied access
        assert data.community_name in self.driver.page_source
        assert "sorter-database_name" not in self.driver.page_source

        # Request access to the community manager
        self.driver.find_element(By.ID, "Iaccept").click()
        self.driver.find_element(By.ID, "community-create-button").click()

        # Home
        self.driver.find_element(By.ID, "home").click()

        # Certify can't OPEN and request is still pending
        assert "OPEN" not in self.driver.page_source
        assert "PENDING" in self.driver.page_source

        # Home
        self.driver.find_element(By.ID, "home").click()

        # Leave community
        self.driver.find_element(By.CSS_SELECTOR, ".btn-link").click()
        self.driver.find_element(By.CSS_SELECTOR, ".bootbox .btn-default").click()

        self.driver.refresh()

        # Certify join button
        assert "JOIN" in self.driver.page_source
        self.driver.find_element(By.LINK_TEXT, "JOIN").click()

        # Save join (request access) page link
        join_link = self.driver.current_url

        # Try community link from when user had access
        self.driver.get(community_link)

        # Certify denied access
        assert "sorter-database_name" not in self.driver.page_source

        # Certify redirect to join page
        assert self.driver.current_url == join_link

        self.utils.logout()

        # Add user to community to keep db state
        self.utils.comm_user_add()
