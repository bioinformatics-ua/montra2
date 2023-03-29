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
import sys

from django.contrib.auth.models import User
from django.db.models import Avg, Count, Max, Min, Sum
from hitcount.models import HitCount

from accounts.models import EmifProfile, NavigationHistory
from community.models import Community, CommunityUser
from fingerprint.models import Answer, Fingerprint


class FingerprintSchemaStats(object):


    def __init__(self, fingerprint_schema):

        """@param fingerprint_schema Receive Questionnarie
        """

        self.fingerprint_schema = fingerprint_schema
        self.calculatUniqueViews()

    def totalDatabases(self):

        q = Fingerprint.getActiveFingerprints(self.fingerprint_schema)
        return q.count()


    def totalDatabaseOwners(self):
        q = Fingerprint.getActiveFingerprints(self.fingerprint_schema)
        return q.count()


    def totalDatabaseShared(self):
        try:
            return Fingerprint.objects.valid(questionnaire=self.fingerprint_schema).annotate(\
                num_shared=Count('shared')).aggregate(Sum('num_shared'))['num_shared__sum']
        except:
            return 0
    def avgDatabaseShared(self):
        return round(Fingerprint.objects.valid(questionnaire=self.fingerprint_schema).annotate(\
            num_shared=Count('shared')).aggregate(Avg('num_shared'))['num_shared__avg'], 2)


    def maxDatabaseShared(self):
        return Fingerprint.objects.valid(questionnaire=self.fingerprint_schema).annotate(\
            num_shared=Count('shared')).aggregate(Max('num_shared'))['num_shared__max']



    def totalFilledQuestions(self):

        #Answer.objects.filter(fingerprint_id__questionnaire=qq).annotate(num_q=Count('question')).aggregate(Sum('num_q'))
        #Answer.objects.filter(fingerprint_id__questionnaire=q).annotate(num_q=Count('question')).aggregate(Sum('num_q'))

        return Answer.objects.filter(\
            fingerprint_id__questionnaire=self.fingerprint_schema).count()


    def maxFilledFingerprints(self):
        return round(Fingerprint.objects.valid(questionnaire=self.fingerprint_schema).aggregate(Max('fill'))['fill__max'], 2)


    def minFilledFingerprints(self):
        return Fingerprint.objects.valid(questionnaire=self.fingerprint_schema).aggregate(Min('fill'))['fill__min']


    def avgFilledFingerprints(self):
        return round(Fingerprint.objects.valid(questionnaire=self.fingerprint_schema).aggregate(Avg('fill'))['fill__avg'], 2)


    def totalDatabaseUsers(self):
        print self.totalDatabaseShared()
        print self.totalDatabaseOwners()
        return self.totalDatabaseShared() + self.totalDatabaseOwners()


    def totalInterested(self):
        #return EmifProfile.objects.filter(interests=self.fingerprint_schema).count()
        #EmifProfile.objects.filter(interests=qq).count()
        cs = Community.objects.filter(questionnaires=self.fingerprint_schema)

        if cs.count() > 0:
            print cs[0]
            return CommunityUser.objects.filter(community=cs[0]).count()


    def maxHitsFingerprints(self):
        return round(Fingerprint.objects.valid(questionnaire=self.fingerprint_schema).aggregate(Max('hits'))['hits__max'],2)


    def minHitsFingerprints(self):
        return Fingerprint.objects.valid(questionnaire=self.fingerprint_schema).aggregate(Min('hits'))['hits__min']


    def avgHitsFingerprints(self):
        return round(Fingerprint.objects.valid(questionnaire=self.fingerprint_schema).aggregate(Avg('hits'))['hits__avg'], 2)

    def totalHitsFingerprints(self):
        return round(Fingerprint.objects.valid(questionnaire=self.fingerprint_schema).aggregate(Sum('hits'))['hits__sum'], 2)

    def calculatUniqueViews(self):
        # Hit does not scale. 
        most_hit = HitCount.objects.all()

        i=0
        counts = 0
        mmax = 0
        mmin = sys.maxint
        self.counts = counts
        self.mmax = mmax
        self.aavg = 0

        for hit in most_hit:
            try:
                this_fingerprint = Fingerprint.objects.valid().get(id=hit.object_pk)
                if this_fingerprint.questionnaire != self.fingerprint_schema:
                    continue
                i = i + 1
                counts += hit.hits
                if (hit.hits>mmax):
                    mmax = hit.hits
                if (hit.hits<mmin):
                    mmin = hit.hits
            except:
                pass
        self.counts = counts
        self.mmax = mmax
        self.aavg = counts/i

        return (i, self.counts, self.aavg, self.mmax, )




    def maxUniqueViewsFingerprints(self):
        return self.mmax


    def avgUniqueViewsFingerprints(self):
        return self.aavg

    def totalUniqueViewsFingerprints(self):
        return self.counts

class FingerprintStats(object):

    def __init__(self, fingerprint):
        pass

    def questions(self):
        pass

# AdvancedQuery.objects.filter(qid=qq).annotate(Count('user')).count()

# QuestionSetCompletion.objects.filter(fingerprint__questionnaire=qq).values('questionset').annotate(fill_avg=Avg('fill'))



class StatisticsView(object):
    def __init__(self):
        pass
    
    def numberOfRegisterUsers(self, community=None,  dateStart=None, dateEnd=None):
        return len(User.objects.filter(date_joined__range=[dateStart, dateEnd]))

    def totalNumberOfRegisterUsers(self, community=None,  dateStart=None, dateEnd=None):
        return len(User.objects.all())
    
    def numberOfUsers(self, community=None):
        users = community.communityuser_set.all().exclude(user__id=-1)
        users.exclude(status=CommunityUser.DISABLED)
        return len(users)
    
    def homePageHits(self, dateStart=None, dateEnd=None):
        history = NavigationHistory.objects.filter(path='index', date__range=[dateStart, dateEnd])
        return len(history)
    def homePageHitsByComm(self, community_slug=None, dateStart=None, dateEnd=None):
        history = NavigationHistory.objects.filter(path='c/'+community_slug, date__range=[dateStart, dateEnd])
        return len(history)

    def numberOfJoins(self, community=None,  dateStart=None, dateEnd=None):
        history = NavigationHistory.objects.filter(path__contains='join', date__range=[dateStart, dateEnd]).filter(path__contains=community)

        return len(history)

    def UsersPerCountry(self, community=None):
        users = community.communityuser_set.all().exclude(user__id=-1)
        users.exclude(status=CommunityUser.DISABLED)

        users_ids = users.values_list("user_id", flat = True)
        users_country = []

        
        users_country = EmifProfile.objects.filter(user_id__in=users_ids).values_list('country').order_by().annotate(Count('country'))

        return users_country
        

    
    def numberOfNewDatabases(self, community,  dateStart, dateEnd):
        pass 

