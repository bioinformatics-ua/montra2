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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from data import MontraTestData as data


class MontraTestUtils(object):

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url

    def login(self, username, password):
        self.driver.get(self.base_url)
        username_box = self.driver.find_element_by_name('identification')
        username_box.send_keys(username)
        password_box = self.driver.find_element_by_name('password')
        password_box.send_keys(password)
        self.driver.find_element_by_tag_name('button').click()

    def logout(self):
        self.driver.get(self.base_url)
        self.driver.find_element_by_id("signout").click()

    def open_community(self):
        self.driver.find_element_by_link_text("OPEN").click()

        # If the community has more than one questionnaire, select the left-most.
        if data.questionnaires["AD Cohort"]["slug"] in self.driver.page_source:
            # click on the first questionnaire of the list view
            self.driver.find_element_by_xpath(
                "//div[@id='pf-list-standard']//div[contains(@class, 'list-group-item')][1]//h4"
            ).click()

    def get_number_of_fingerprints(self):

        # Click "Show All"
        dropdown = self.driver.find_element_by_css_selector(".paginator-page-selector")
        dropdown.find_element_by_xpath("//option[. = 'All']").click()

        # Get number of fingerprints
        count = len(self.driver.find_elements_by_xpath("//table[@id='table_databases']/tbody/tr"))
        return count

    def wait_element_clickable(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            expected_conditions.element_to_be_clickable(locator))

    def wait_element_invisible(self, locator, timeout=10):
        self.driver.implicitly_wait(0)
        WebDriverWait(self.driver, timeout).until(
            expected_conditions.invisibility_of_element_located(locator))
        self.driver.implicitly_wait(10)

    def comm_user_remove(self):
        user1 = data.users["user1"]
        user2 = data.users["user2"]

        # Login as user2
        self.login(user2["username"], user2["password"])

        # Click "Admin panel"
        self.driver.find_element(By.ID, "admin").click()

        # Click on community app models section
        self.driver.find_element(By.LINK_TEXT, "Community").click()

        # Community users
        self.driver.find_element(By.XPATH, "//strong[contains(.,\'Community users\')]").click()

        # Order by user
        self.driver.find_element(By.LINK_TEXT, "User").click()

        # Click on first user
        self.driver.find_element(By.LINK_TEXT, "test_community").click()

        assert user1["username"] in self.driver.page_source

        self.driver.find_element(By.LINK_TEXT, "Delete").click()

        self.driver.find_element(By.XPATH, "//input[@value=\"Yes, I\'m sure\"]").click()

        assert "deleted successfully" in self.driver.page_source

        # Switch back to landing page
        self.driver.get(self.base_url)

        self.logout()

    def comm_user_add(self):
        user1 = data.users["user1"]
        user2 = data.users["user2"]

        # Login as user2
        self.login(user2["username"], user2["password"])

        # Click "Admin panel"
        self.driver.find_element(By.ID, "admin").click()

        # Click on community app models section
        self.driver.find_element(By.LINK_TEXT, "Community").click()

        # Community users
        self.driver.find_element(By.XPATH, "//strong[contains(.,\'Community users\')]").click()

        assert user1["username"] not in self.driver.page_source

        # Add
        self.driver.find_element(By.LINK_TEXT, "Add community user").click()

        dropdown = self.driver.find_element(By.ID, "id_community")
        dropdown.find_element(By.XPATH, "//option[. = 'test_community']").click()
        dropdown = self.driver.find_element(By.ID, "id_user")
        dropdown.find_element(By.XPATH, "//option[. = 'user1']").click()
        dropdown = self.driver.find_element(By.ID, "id_status")
        dropdown.find_element(By.XPATH, "//option[. = 'Enabled in community']").click()

        self.driver.find_element(By.NAME, "_save").click()

        assert user1["username"] in self.driver.page_source

        # Switch back to landing page
        self.driver.get(self.base_url)

        self.logout()

    def verfiy_access_to_all_qsets(self, current_fingerprint_acronym):

        # Open fingerprint
        self.driver.find_element(By.CSS_SELECTOR, "a[data-acronym={}]".format(current_fingerprint_acronym)).click()

        # Wait for contents to appear
        WebDriverWait(self.driver, 20).until(
            expected_conditions.visibility_of_element_located((By.ID, "question_1.01"))
        )

        # Verify contents of question_set 1
        assert current_fingerprint_acronym in self.driver.page_source
        assert data.fingerprint_name in self.driver.page_source
        assert "test question_1.07.04" in self.driver.page_source

        # Click on question_set 2, wait, and verify contents
        self.driver.find_element(By.ID, "counter1_2").click()
        self.driver.find_element(By.ID, "question_2.01")
        assert "test question_2.05_more1" in self.driver.page_source
        assert "Aveiro" in self.driver.page_source
        assert "Portugal" in self.driver.page_source

        # Click on question_set 4, wait, and verify contents
        self.driver.find_element(By.ID, "counter1_4").click()
        self.driver.find_element(By.ID, "question_4.01")
        assert "test question_4.01" in self.driver.page_source
        assert "test question_4.06" in self.driver.page_source

        # Click on question_set 5, wait, and verify contents
        self.driver.find_element(By.ID, "counter1_5").click()
        self.driver.find_element(By.ID, "question_5.03")
        assert "test question_5.05" in self.driver.page_source
        assert "test question_5.11" in self.driver.page_source

        # Click on question_set 6, wait, and verify contents
        self.driver.find_element(By.ID, "counter1_6").click()
        self.driver.find_element(By.ID, "question_601_pubmedid")
        assert "test question_601_pubauthors" in self.driver.page_source
        assert "test question_6.03\ntest question_6.03" in self.driver.page_source

        # Click on question_set 1, wait, and verify contents
        self.driver.find_element(By.ID, "counter1_1").click()
        self.driver.find_element(By.ID, "question_1.01")
        assert data.fingerprint_name in self.driver.page_source
        assert "test question_1.07.04" in self.driver.page_source

    def click_table_item(self, table_id, header_name, tr_xpath, item_xpath):
        """
        Clicks a specific element inside a table cell.

        Args:
            table_id (str): html element id
            header_name (str): text of the header of the column that contains the element to click
            tr_xpath (str): xpath inside the tbody element that should select the tr that contains the element to click
            item_xpath (str): xpath to the element to click, inside the respective td element
        """
        headers = self.driver.find_elements_by_xpath('//table[@id="{}"]/thead//th'.format(table_id))
        column_index = next(i for i, header in enumerate(headers) if header.text.strip() == header_name)
        self.driver.find_element(
            By.XPATH,
            '//table[@id="{}"]/tbody//{}/td[{}]//{}'.format(table_id, tr_xpath, column_index + 1, item_xpath)
        ).click()

    def check_job_output_file(self, file_finder, download_path, allowed):
        """
        Checks if the user was able to export, or not, a given file through a job.
        If allowed=True the file should be found, else the job wasn't created then no file should return True
          on the file_finder function.

        Args:
            file_finder (function): receives the a filename as argument and returns True if the given
              file is the expected one.
            download_path (str): where the file must be downloaded to
            allowed (bool): if the user has permissions to download the file
        """
        # Click "here" when it appears
        element = self.wait_element_clickable((By.LINK_TEXT, "here"))
        element.click()

        # Wait export job is done
        start_time = time.time()
        while True:

            if "Job is being executed" not in self.driver.page_source:
                break
            else:
                self.driver.refresh()

            assert time.time() - start_time < 10, "Export job not done after 10 seconds"

        # Click "Download" when it appears
        element = self.wait_element_clickable((By.LINK_TEXT, "Download"))
        element.click()

        time.sleep(5)
        # Verify that the file was downloaded
        found = any(file_finder(f) for f in os.listdir(download_path))

        if allowed:
            assert found
        else:
            assert not found

        # Remove files
        if found:
            for f in os.listdir(download_path):
                if file_finder(f):
                    os.remove(os.path.join(download_path, f))
