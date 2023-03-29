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


class MontraTestData(object):

    community_name = "test_community"
    plugin_name = "test_plugin"
    group_name = "test_group"
    fingerprint_acronym = "test_fingerprint_"
    fingerprint_name = "fingerprint_test_name"
    fingerprint_institution = "fingerprint_test_institution"

    questionnaires = {"EHDEN_final": {"file_name": "EHDEN_final.xlsx",
                                      "slug": "ehden_final"},

                      "AD Cohort": {"file_name": "AD Cohort.xlsx",
                                    "slug": "ad-cohort"}}

    users = {"user1": {"username": "user1",
                       "password": "test123",
                       "email": "user1@emiftest.pt",
                       "first_name": "user1Fname",
                       "last_name": "user1Lname",
                       "is_superuser": False},

             "user2": {"username": "user2",
                       "password": "test123",
                       "email": "user2@emiftest.pt",
                       "first_name": "user2Fname",
                       "last_name": "user2Lname",
                       "is_superuser": True}}
