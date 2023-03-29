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
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from utils.testcases import MontraTestCase
from utils.data import MontraTestData as data


class QuestionnaireImportTest(MontraTestCase):

    def test_questionnaire_import(self):

        user2 = data.users["user2"]

        self.utils.login(user2["username"], user2["password"])

        # Make sure user has import access
        assert 'Import' in self.driver.page_source

        import_button = self.driver.find_element(By.ID, "import")
        self.driver.execute_script("arguments[0].scrollIntoView();", import_button)

        # Mouse over Import
        actions = ActionChains(self.driver)
        actions.move_to_element(import_button).perform()
        self.driver.find_element(By.ID, "import").click()

        # Click "Import Questionnaire"
        self.driver.find_element(By.XPATH, "//a[contains(@href, \'questionnaire/import\')]").click()

        assert 'Aborted' not in self.driver.page_source

        questionnaire_file = None

        for q in data.questionnaires.values():
            if q["file_name"] not in self.driver.page_source:
                questionnaire_file = q["file_name"]
                questionnaire_slug = q["slug"]
                break

        assert questionnaire_file is not None, "All questionnaires are already inserted"

        parent_path = os.path.dirname(os.getcwd())

        questionnaire_path = os.path.join(parent_path, 'questionnaires', questionnaire_file)

        # Click "Select a file" and select a file locally
        self.driver.find_element_by_id("my-file").send_keys(questionnaire_path)

        # Click "Preview"
        self.driver.find_element(By.NAME, "action").click()

        while True:
            if "/questionnaire/import" in self.driver.current_url:
                # Check not aborted due duplicate key
                assert 'Aborted' not in self.driver.page_source
            elif "/fingerprint/" in self.driver.current_url:
                break

            time.sleep(0.5)

        # Click "OK"
        self.driver.find_element(By.ID, "preview-ok").click()

        while True:
            if "/questionnaire/import" in self.driver.current_url:
                break

            time.sleep(0.5)

        # Check if the questionnaire upload was done correctly
        assert questionnaire_file in self.driver.page_source
        assert 'Finished' in self.driver.page_source
        assert 'Aborted' not in self.driver.page_source

        # # Associate imported questionnaire to test community
        self.driver.get(self.base_url)

        # Click "Admin panel"
        self.driver.find_element(By.ID, "admin").click()

        self.driver.find_element(By.LINK_TEXT, "Community").click()
        self.driver.find_element(By.XPATH, "//div[@id=\'app_community\']/div/a/strong").click()
        self.driver.find_element(By.LINK_TEXT, "testcommunity").click()
        dropdown = self.driver.find_element(By.ID, "id_questionnaires")

        questionnaire_name = questionnaire_file.split('.')[0]
        dropdown.find_element(By.XPATH, "//option[. = '{}']".format(questionnaire_name)).click()

        self.driver.find_element(By.NAME, "_save").click()

        # Switch back to landing page
        self.driver.get(self.base_url)

        # Open community
        self.driver.find_element(By.LINK_TEXT, "OPEN").click()

        assert questionnaire_slug in self.driver.page_source
