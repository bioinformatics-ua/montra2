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

import argparse
import sys
from unittest import TestLoader, TestSuite, TextTestRunner
from HtmlTestRunner import HTMLTestRunner
from utils.testcases import MontraTestCase

from emif.test_login import LoginTestCase
from emif.test_flatpages import FlatpagesTestCase
from questionnaire.test_questionnaire_import import QuestionnaireImportTest
from searchengine.test_search_engine import SearchEngineTestCase
from fingerprint.test_fingerprint_add import FingerprintAddTestCase
from fingerprint.test_fingerprint_share_ownership import FingerprintShareOwnershipTestCase
from fingerprint.test_fingerprint_share_ownership_draft import FingerprintShareOwnershipDraftTestCase
from fingerprint.test_fingerprint_publish import FingerprintPublishTestCase
from fingerprint.test_fingerprint_access_control import FingerprintAccessControlTestCase
from fingerprint.test_fingerprint_private_link import FingerprintPrivateLinkTestCase
from fingerprint.test_fingerprint_search import FingerprintSearchTestCase
from fingerprint.test_fingerprint_listing import FingerprintListingTestCase
from fingerprint.test_fingerprint_views import FingerprintViewsTestCase
from fingerprint.test_fingerprint_filters import FingerprintFilterTestCase
from fingerprint.test_fingerprint_delete import FingerprintDeleteTestCase
from community.test_community_access_control import CommunityAccessControlTestCase
from community.test_qsets_permissions import QSetsPermissionsTestCase
from community.test_plugin_add import PluginAddTestCase
from community.test_group_add import GroupAddTestCase
from community.test_group_plugin_permissions import GroupPluginPermissionsTestCase
from community.test_group_api import GroupAPITestCase
from community.test_group_editors import GroupEditorsTestCase


TEST_CLASSES = [
    LoginTestCase,
    FlatpagesTestCase,
    QuestionnaireImportTest,
    CommunityAccessControlTestCase,
    FingerprintAddTestCase,
    FingerprintShareOwnershipDraftTestCase,
    FingerprintPublishTestCase,
    FingerprintShareOwnershipTestCase,
    PluginAddTestCase,
    QSetsPermissionsTestCase,
    FingerprintAccessControlTestCase,
    FingerprintPrivateLinkTestCase,
    FingerprintSearchTestCase,
    SearchEngineTestCase,
    GroupAddTestCase,
    GroupPluginPermissionsTestCase,
    GroupAPITestCase,
    GroupEditorsTestCase,
    QuestionnaireImportTest,
    FingerprintAddTestCase,
    FingerprintPublishTestCase,
    FingerprintListingTestCase,
    FingerprintViewsTestCase,
    FingerprintFilterTestCase,
    FingerprintDeleteTestCase,
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-tr', '--text_runner', action='store_true',
                        help='Use TextTestRunner (default: Use HTMLTestRunner)')
    parser.add_argument('-hl', '--headless', action='store_true',
                        help='Use browser headless mode (default: Normal mode.)')
    parser.add_argument('-b', '--base_url', default='http://localhost:8181',
                        help='Base URL (default: http://localhost:8181)')
    parser.add_argument('-t', '--single_test', default=None,
                        help='Test to run (default: Run all tests.)')
    parser.add_argument('-l', '--load_fixtures', action='store_true',
                        help='Load fixtures before test (default: False)')
    parser.add_argument('-d', '--dump_fixtures', action='store_true',
                        help='Dump fixtures before test (default: False)')
    args = parser.parse_args()

    MontraTestCase.headless = args.headless
    MontraTestCase.base_url = args.base_url
    MontraTestCase.load_fixtures = args.load_fixtures
    MontraTestCase.dump_fixtures = args.dump_fixtures

    tests_list = []

    if args.single_test:
        for test_class in TEST_CLASSES:
            if test_class.__name__ == args.single_test:
                tests_from_class = TestLoader().loadTestsFromTestCase(test_class)
                tests_list.append(tests_from_class)
                break
    else:
        test_classes = TEST_CLASSES

        if MontraTestCase.load_fixtures:
            # Removing duplicates, maintaining tests order
            seen = set()
            seen_add = seen.add
            test_classes = [x for x in TEST_CLASSES if not (x in seen or seen_add(x))]

        for test_class in test_classes:
            tests_from_class = TestLoader().loadTestsFromTestCase(test_class)
            tests_list.append(tests_from_class)

    test_suite = TestSuite(tests_list)

    if args.text_runner:
        results = TextTestRunner(verbosity=2).run(test_suite)
    else:

        title = "Montra Test Results"

        if MontraTestCase.load_fixtures:
            title += " - Load"
        if MontraTestCase.dump_fixtures:
            title += " - Dump"
        if MontraTestCase.headless:
            title += " - Headless"

        title += " - {}".format(MontraTestCase.base_url)

        results = HTMLTestRunner(output='test_results', combine_reports=True,
                       report_name='MontraTestResults', report_title=title).run(test_suite)

    if results.errors or results.failures:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
