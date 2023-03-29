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

import os
import subprocess
from unittest import TestCase
from selenium import webdriver

from utils import MontraTestUtils


class MontraTestCase(TestCase):

    base_url = 'http://localhost:8181'
    headless = False
    dump_fixtures = False
    load_fixtures = False

    def setUp(self):

        if self.dump_fixtures:
            self.dumpFixtures()

        if self.load_fixtures:
            self.loadFixtures()

        options = webdriver.chrome.options.Options()
        options.add_argument("--window-size=1366,900")

        self.download_path = os.getcwd()
        prefs = {'download.default_directory': self.download_path}
        options.add_experimental_option('prefs', prefs)

        if self.headless:
            options.add_argument('--headless')
            options.add_argument("--no-sandbox")

        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)
        # self.driver.maximize_window() # do not work in headless mode

        self.utils = MontraTestUtils(self.driver, self.base_url)

    def tearDown(self):
        self.driver.quit()

    def dumpFixtures(self):
        cmd = "python manage.py dumpdata --natural-foreign --exclude auth.permission --exclude contenttypes --indent 4 > fixtures/test_fixtures/{}.json".format(
            self.__class__.__name__)
        subprocess.check_output(cmd, shell=True, cwd='/deploy/catalogue/emif')

    def loadFixtures(self):
        cmd = "python manage.py flush --noinput; python manage.py loaddata fixtures/test_fixtures/{}.json; python manage.py index_all; python manage.py check_permissions".format(
            self.__class__.__name__)
        subprocess.check_output(cmd, shell=True, cwd='/deploy/catalogue/emif')
