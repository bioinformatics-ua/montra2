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

from utils.testcases import MontraTestCase
from utils.data import MontraTestData as data


class LoginTestCase(MontraTestCase):

    def test_login(self):

        user = data.users["user1"]

        # access login page, fill login form and submit it!
        self.utils.login(user["username"], user["password"])

        # check the returned result
        assert 'user_name_div' in self.driver.page_source
        assert user["first_name"] in self.driver.page_source
        assert user["last_name"] in self.driver.page_source
