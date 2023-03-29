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


class FingerprintAccessControlTestCase(MontraTestCase):

    def test_fingerprint_access_control(self):

        user1 = data.users["user1"]

        # Login as user1
        self.utils.login(user1["username"], user1["password"])

        self.utils.open_community()

        count = self.utils.get_number_of_fingerprints()

        current_fingerprint_acronym = data.fingerprint_acronym + str(count)

        # Certify access to fingerprint
        assert 'data-acronym="' + current_fingerprint_acronym in self.driver.page_source

        # Open fingerprint
        self.driver.find_element(By.CSS_SELECTOR, "a[data-acronym={}]".format(current_fingerprint_acronym)).click()

        # Certify access
        assert current_fingerprint_acronym in self.driver.page_source

        # Save fingerprint link
        fingerprint_link = self.driver.current_url

        self.utils.logout()

        # Remove user1 from community
        self.utils.comm_user_remove()

        # Login as user1
        self.utils.login(user1["username"], user1["password"])

        # Certify join button (user not in community)
        assert "JOIN" in self.driver.page_source

        self.driver.find_element(By.LINK_TEXT, "JOIN").click()

        # Certify denied access
        assert 'data-acronym="' + current_fingerprint_acronym not in self.driver.page_source

        # Save join (request access) page link
        join_link = self.driver.current_url

        # Try fingerprint link from when user had access
        self.driver.get(fingerprint_link)

        # Certify denied access
        assert current_fingerprint_acronym not in self.driver.page_source

        # Certify redirect to join page
        assert self.driver.current_url == join_link

        self.utils.logout()

        # Add user to community to keep db state
        self.utils.comm_user_add()
