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
#
from django.contrib.auth.models import User

from community.models import Community, CommunityUser
from questionnaire.models import Questionnaire
from django.db import transaction

# Owners should be determined, for now admin is the owner
communities = {
    'observational': {
        'questionnaires': [49],
        'owners': ['admin'],
        'name': 'EMIF OD',
        'description': '''In EMIF/Platform, a number of organisations who are able to provide data for research are working together towards an infrastructure to facilitate re-use of medical data.
These organisations provide access to one or more data bases''',
    },
    'adcohort': {
        'questionnaires': [53],
        'owners': ['admin'],
        'name': 'EMIF AD',
        'description': '''<p>The <strong>overall aim of EMIF-AD </strong>is to build an IF for studies on neurodegeneration in order to discover and validate AD biomarkers for the facilitation of drug development and trial design in predementia AD. Our main objectives are:</p>
<ol><li>To set-up a large data repository of patient data to allow biomarker discovery studies within the EMIF; this will facilitate large-scale biomarker discovery and replication studies.</li>
<li>To link data from research cohorts to electronic health registry data and use to electronic health registry data to define extreme phenotypes.</li>
<li>To discover and validate new biomarkers in plasma, cerebrospinal fluid and using MRI for the diagnosis and prognosis of AD in the presymptomatic and prodromal stage using the extreme phenotype approach.</li>
<li>To identify new potential targets for AD drug development using genomics and proteomics approaches in presymptomatic and prodromal AD.</li>
</ol><p>To test the utility of the new biomarkers for selection of subjects for AD prevention trials; this will give proof-of-concept data on whether the new biomarkers facilitate trial design.</p>'''
    },
    'epad': {
        'questionnaires': [55],
        'owners': ['admin'],
        'name': 'EPAD',
        'description': '''The European Prevention of Alzheimer's Dementia (EPAD) project aims to develop an infrastructure that efficiently enables the undertaking of adaptive, multi-arm Proof of Concept studies for early and accurate decisions on the ongoing development of drug candidates or drug combinations.

This includes evaluating patients' reactions to a drug early in a clinical trial and modifying the trial according to these reactions. The EPAD project will initially run for five years.

The platform will draw European participants, whose records are already part of existing national/regional cohort or register studies, into an EPAD register of approximately 24,000 people. From this group, 6,000 people will be asked to join a pan-European EPAD Cohort for consistent, longitudinal follow-up, and approximately 1,500 of them will eventually be invited to enter the standing EPAD Proof of Concept Trial.

This approach aims to ensure EPAD has access to an at-risk population showing biomarker evidence of Alzheimer's disease prior to the development of dementia.
'''
    }
}

@transaction.atomic
def createCommunities():

    for community, details in communities.items():
        try:
            c = Community.objects.get(slug=community)

            raise Exception('ERROR: Community %s already exists, this script has been ran already, or something is wrong.' % community)
        except Community.DoesNotExist:
            c = Community(slug=community, name=details['name'], description=details['description'])
            c.save()

            for user in details['owners']:
                try:

                    usr = User.objects.get(username=user)
                    c.owners.add(usr)

                except User.DoesNotExist:
                    raise Exception('ERROR: Could not find user with username %s' % user)

            for questionnaire in details['questionnaires']:
                try:

                    usr = Questionnaire.objects.get(id=questionnaire)
                    c.questionnaires.add(usr)

                except Questionnaire.DoesNotExist:
                    raise Exception('ERROR: Could not find user with id %s' % questionnaire)

            #addAllUsers(c)

def addAllUsers(community):
    everyone = User.objects.all()

    for user in everyone:
        cu = CommunityUser(community = community, user=user, status=CommunityUser.ENABLED)

        cu.save()

createCommunities()
