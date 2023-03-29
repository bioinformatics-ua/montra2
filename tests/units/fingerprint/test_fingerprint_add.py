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

import time
from selenium.webdriver.common.by import By

from utils.testcases import MontraTestCase
from utils.data import MontraTestData as data


class FingerprintAddTestCase(MontraTestCase):

    def test_fingerprint_add(self):

        user2 = data.users["user2"]

        self.utils.login(user2["username"], user2["password"])

        assert 'New Entry' not in self.driver.page_source

        self.utils.open_community()

        assert 'New Entry' in self.driver.page_source

        count = self.utils.get_number_of_fingerprints()

        current_fingerprint_acronym = data.fingerprint_acronym + str(count + 1)

        assert current_fingerprint_acronym not in self.driver.page_source

        databases_button = self.driver.find_element(By.ID, "databases")
        databases_button.click()
        databases_button.find_element(By.XPATH, '../../ul//a[text()[contains(., "New Entry")]]').click()

        # Wait for modal to appear
        element = self.utils.wait_element_clickable((By.CSS_SELECTOR, ".bootbox .btn"))

        # Click on "Close"
        element.click()

        # Wait for modal to disappear
        self.utils.wait_element_invisible((By.CSS_SELECTOR, ".bootbox .btn"))

        self.driver.find_element(By.LINK_TEXT, "Next").click()

        # Page 1
        self.driver.find_element(By.ID, "question_1.01").send_keys(current_fingerprint_acronym)
        self.driver.find_element(By.ID, "question_1.02").send_keys(data.fingerprint_name)
        self.driver.find_element(By.ID, "question_1.03").send_keys(data.fingerprint_institution)
        self.driver.find_element(By.ID, "question_1.04").send_keys("test question_1.04")
        self.driver.find_element(By.ID, "question_1.05").send_keys("http://test105.com")
        self.driver.find_element(By.ID, "question_1.06").send_keys("http://test106.com")
        self.driver.find_element(By.ID, "question_1.07.01").send_keys("test question_1.07.01")
        self.driver.find_element(By.ID, "question_1.07.02").send_keys("test question_1.07.02")
        self.driver.find_element(By.ID, "question_1.07.03").send_keys("test10703@ua.random")
        self.driver.find_element(By.ID, "question_1.07.04").send_keys("test question_1.07.04")
        self.driver.find_element(By.ID, "question_1.08.01").send_keys("test question_1.08.01")
        self.driver.find_element(By.ID, "question_1.08.02").send_keys("test question_1.08.02")
        self.driver.find_element(By.ID, "question_1.08.03").send_keys("test10803@ua.random")
        self.driver.find_element(By.ID, "question_1.08.04").send_keys("test question_1.08.04")
        self.driver.find_element(By.ID, "question_1.09.01").send_keys("test question_1.09.01")
        self.driver.find_element(By.ID, "question_1.09.02").send_keys("test question_1.09.02")
        self.driver.find_element(By.ID, "question_1.09.03").send_keys("test10903@ua.random")
        self.driver.find_element(By.ID, "question_1.09.04").send_keys("test question_1.09.04")
        self.driver.find_element(By.ID, "question_1.10.01").send_keys("test question_1.10.01")
        self.driver.find_element(By.ID, "question_1.10.02").send_keys("test question_1.10.02")
        self.driver.find_element(By.ID, "question_1.10.03").send_keys("test11003@ua.random")
        self.driver.find_element(By.ID, "question_1.10.04").send_keys("test question_1.07.04")
        self.driver.find_element(By.LINK_TEXT, "Next").click()

        assert 'Errors' not in self.driver.page_source

        # Page 2
        self.driver.find_element(By.ID, "question_2.01").send_keys("test question_2.01")

        self.driver.find_element(By.NAME, "question_2.02_more1").send_keys("test question_2.02_more1")
        self.driver.find_element(By.ID, "question_2.02_multiple_2").click()
        self.driver.find_element(By.ID, "question_2.02_multiple_6").click()

        self.driver.find_element(By.NAME, "question_2.05_more1").send_keys("test question_2.05_more1")

        element_to_scroll = self.driver.find_element(By.ID, "question_2.03_yes")
        self.driver.execute_script("arguments[0].scrollIntoView();", element_to_scroll)

        self.driver.find_element(By.ID, "question_2.03_yes").click()
        self.driver.find_element(By.ID, "question_2.04_2").click()
        self.driver.find_element(By.ID, "question_2.05_multiple_1").click()
        self.driver.find_element(By.ID, "question_2.05_multiple_4").click()

        elements_list = self.driver.find_elements(By.CSS_SELECTOR, ".btn-group:nth-child(2) > .btn")

        assert elements_list, "Could not find country dropdown, maybe check the network requisite."

        element_to_scroll = self.driver.find_element(By.CSS_SELECTOR, ".btn-group:nth-child(2) > .btn")
        self.driver.execute_script("arguments[0].scrollIntoView();", element_to_scroll)

        # Portugal
        self.driver.find_element(By.CSS_SELECTOR, ".btn-group:nth-child(2) > .btn").click()
        self.driver.find_element(By.CSS_SELECTOR, ".open > .dropdown-menu .form-control").send_keys("port")
        self.driver.find_element(By.LINK_TEXT, "Portugal").click()

        # Distrito de Aveiro
        self.driver.find_element(By.CSS_SELECTOR, ".btn-group:nth-child(3) .filter-option").click()
        self.driver.find_element(By.CSS_SELECTOR, ".btn-group:nth-child(3) li:nth-child(4) .text").click()

        self.driver.find_element(By.NAME, "question_2.07_more1").send_keys("test question_2.07_more1")
        self.driver.find_element(By.CSS_SELECTOR, "#answer_2\\.07 li:nth-child(1) .checkbox-label").click()

        self.driver.find_element(By.ID, "question_2.08").send_keys("test question_2.08")
        self.driver.find_element(By.NAME, "question_2.09_more1").send_keys("test question_2.09_more1")
        self.driver.find_element(By.CSS_SELECTOR, "#answer_2\\.09 li:nth-child(2) .checkbox-label").click()
        self.driver.find_element(By.CSS_SELECTOR, "#answer_2\\.09 li:nth-child(3) .checkbox-label").click()

        self.driver.find_element(By.NAME, "question_2.10_more1").send_keys("test question_2.10_more1")
        self.driver.find_element(By.CSS_SELECTOR, "#answer_2\\.10 li:nth-child(2) .checkbox-label").click()
        self.driver.find_element(By.CSS_SELECTOR, "#answer_2\\.10 li:nth-child(6) .checkbox-label").click()

        self.driver.find_element(By.NAME, "question_2.11_more1").send_keys("test question_2.11_more1")
        self.driver.find_element(By.CSS_SELECTOR, "#answer_2\\.11 li:nth-child(3) .checkbox-label").click()
        self.driver.find_element(By.CSS_SELECTOR, "#answer_2\\.11 li:nth-child(4) .checkbox-label").click()

        self.driver.find_element(By.NAME, "question_2.12_more1").send_keys("test question_2.12_more1")
        self.driver.find_element(By.CSS_SELECTOR, "#answer_2\\.12 li:nth-child(2) .checkbox-label").click()

        self.driver.find_element(By.ID, "question_2.13").send_keys("test question_2.13")
        self.driver.find_element(By.LINK_TEXT, "Next").click()

        # Page 4
        self.driver.find_element(By.ID, "question_4.01").send_keys("test question_4.01")
        self.driver.find_element(By.CSS_SELECTOR, "#datepicker_4\\.02 .glyphicon").click()

        self.driver.find_element(By.NAME, "question_4.04_more1").send_keys("test question_4.04_more1")
        self.driver.find_element(By.CSS_SELECTOR, "#datepicker_4\\.03 > .input-group-addon").click()
        self.driver.find_element(By.CSS_SELECTOR, "#answer_4\\.04 li:nth-child(2) .checkbox-label").click()

        self.driver.find_element(By.ID, "question_4.05").send_keys("test question_4.05")
        self.driver.find_element(By.ID, "question_4.06").send_keys("test question_4.06")
        self.driver.find_element(By.ID, "question_4.07").send_keys("test question_4.07")
        self.driver.find_element(By.LINK_TEXT, "Next").click()

        # Page 5
        self.driver.find_element(By.CSS_SELECTOR, "#answer_5\\.01 li:nth-child(2) .radiobox-label").click()

        self.driver.find_element(
            By.CSS_SELECTOR, "#answer_5\\.02 .questionnaire-choice-checkbox > .radiobox-label").click()
        self.driver.find_element(By.ID, "question_5.03").send_keys("test question_5.03")
        self.driver.find_element(By.ID, "question_5.04").send_keys("3.5")
        self.driver.find_element(By.ID, "question_5.05").send_keys("test question_5.05")
        self.driver.find_element(By.ID, "question_5.06").send_keys("test question_5.06")
        self.driver.find_element(By.ID, "question_5.07").send_keys("test question_5.07")

        self.driver.find_element(By.ID, "question_5.11").send_keys("test question_5.11")
        self.driver.find_element(By.ID, "question_5.08_yes").click()
        self.driver.find_element(By.CSS_SELECTOR, "#answer_5\\.09 li:nth-child(2) .radiobox-label").click()
        self.driver.find_element(
            By.CSS_SELECTOR, "#answer_5\\.10 .questionnaire-choice-checkbox > .radiobox-label").click()

        self.driver.find_element(By.LINK_TEXT, "Next").click()

        # Page 6
        self.driver.find_element(By.ID, "question_601_pubmedid").send_keys("test question_601_pubmedid")
        self.driver.find_element(By.ID, "question_601_pubtitle").send_keys("test question_601_pubtitle")
        self.driver.find_element(By.ID, "question_601_pubauthors").send_keys("test question_601_pubauthors")
        self.driver.find_element(By.ID, "question_601_pubjournal").send_keys("test question_601_pubjournal")
        self.driver.find_element(By.ID, "question_601_pubyear").send_keys("2006")

        self.driver.find_element(By.NAME, "question_6.02_more1").send_keys("test question_6.02_more1")
        self.driver.find_element(By.ID, "addpub").click()

        self.driver.find_element(By.CSS_SELECTOR, "#answer_6\\.02 li:nth-child(1) .checkbox-label").click()

        self.driver.find_element(By.ID, "question_6.03").send_keys("test question_6.03\ntest question_6.03")
        self.driver.find_element(By.CSS_SELECTOR, "#answer_6\\.02 li:nth-child(6) .checkbox-label").click()

        # Submit btn
        self.driver.find_element(By.CSS_SELECTOR, "#qform6 > .well .btn:nth-child(3)").click()

        # Home
        self.driver.find_element(By.ID, "home").click()

        self.utils.open_community()

        # # Enter in fingerprint to verify inserted contents

        # Wait for fingerprint indexing
        start_time = time.time()
        while True:

            if current_fingerprint_acronym in self.driver.page_source:
                break
            else:
                self.driver.refresh()

            assert time.time() - start_time < 10, "Fingerprint not indexed after 10 seconds"

        self.utils.verfiy_access_to_all_qsets(current_fingerprint_acronym)
