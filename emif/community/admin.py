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
from django.contrib import admin
from django.contrib.auth.models import User
from adminplus.sites import AdminSitePlus

from .models import *


from accounts.models import Profile, NavigationHistory, EmifProfile
from django.contrib import admin
from django.contrib.auth.models import User
from adminplus.sites import AdminSitePlus

from django.shortcuts import render

from django.forms import ModelForm, ModelChoiceField

from django import forms
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

from django.db.models import Count, Avg, Max, Min

from django.utils import timezone
import datetime

from accounts.models import RestrictedUserDbs, RestrictedGroup
from fingerprint.models import Fingerprint
from hitcount.models import Hit, HitCount


# Too many for inline, inline would need pagination which is not possible by default
#class CommunityUserInline(admin.TabularInline):
#    model = CommunityUser


class CommunityUserAdmin(admin.ModelAdmin):
    list_display = ['community', 'user', 'status']

class CommunitiesFavoritedAdmin(admin.ModelAdmin):
    list_display = ['community', 'user']


class CommunityAdmin(admin.ModelAdmin):
    list_display = ['slug', 'name', 'description', 'public', 'auto_accept']

class CommunityPermissionAdmin(admin.ModelAdmin):
    list_display = ['communitygroup', 'plugin', 'allow']


# ********************************************************************
# *** this will eventually be deleted
class CommunityGroupAdmin(admin.ModelAdmin):
    list_display = ['community', 'name', 'description', 'removed']

class CommunityDatabasePermissionAdmin(admin.ModelAdmin):
    list_display = ['communitygroup', 'plugin', 'database', 'allow']
    
class CommunityFieldsAdmin(admin.ModelAdmin):
    list_display = [f.name for f in CommunityFields._meta.get_fields()]
# ********************************************************************
# *** 

class ExternalCommunityAdmin(admin.ModelAdmin):
    list_display = [f.name for f in ExternalCommunity._meta.get_fields()]

################################################################################################
# Statistics by Community 
################################################################################################
class ChoiceForm(forms.Form):
    community = forms.ModelChoiceField(Community.objects.all())

class CommunityStatistics(View):
    template_name = 'admin/community_statistics.html'

    def get(self, request):
        form = ChoiceForm()

        history = NavigationHistory.objects.all()

        most_viewed = history.values('path').annotate(number_viewed=Count('path')).order_by('-number_viewed')[:15]

        session_time, average_time = self.getSessionTimes(history)

        views_time, average_views = self.getViewTimes(history)

        return render(request, self.template_name, {'choice': form, 'global': True,
                                                    'most_viewed': most_viewed,
                                                    'session_time': session_time,
                                                    'session_average': average_time,
                                                    'views_time': views_time,
                                                    'views_average': average_views,
                                                    'top_users': EmifProfile.top_users(limit=20, days_to_count=30)
                                                    })

    def post(self, request):
        community_id = request.POST.get('community', -1)
        # Select community 
        community = Community.objects.get(id=community_id)
        form = ChoiceForm(initial = {'Community': community})
        
        # Filter by community, probably a better workaround is needed. 
        user_history = NavigationHistory.objects.filter(path__icontains=community.slug)

        most_viewed = user_history.values('path').annotate(number_viewed=Count('path')).order_by('-number_viewed')[:15]

        session_time, average_time = self.getSessionTimes(user_history)

        views_time, average_views = self.getViewTimes(user_history)
        database_hits, avg_hits = self.databaseHits(community)

        return render(request, self.template_name, {'choice': form, 'global': False,
                                                    'most_viewed': most_viewed,
                                                    'session_time': session_time,
                                                    'session_average': average_time,
                                                    'views_time': views_time,
                                                    'views_average': average_views,
                                                    'database_hits': database_hits,
                                                    'top_users': EmifProfile.top_users(limit=20, days_to_count=30)
                                                    })

    def getSessionTimes(self, user_history):

        session_times = []
        average = 0
        d = timezone.now().date()
        end_date = (timezone.now()-datetime.timedelta(days=365)).date()

        delta = datetime.timedelta(days=30)
        while d >= end_date:

            user_day_history = user_history.filter(date__startswith=d)

            min = user_day_history.aggregate(Min('date'))['date__min']
            max = user_day_history.aggregate(Max('date'))['date__max']

            try:
                session = (max-min).total_seconds() / 3600

                average += session

                session_times.append({ 'label': d.strftime('%B'), 'value': session })
            except:
                session_times.append({ 'label': d.strftime('%B'), 'value': 0 })

            d -= delta

        return [session_times[::-1], average]

    def getViewTimes(self, user_history):

        view_times = []
        average = 0
        d = timezone.now().date()
        end_date = (timezone.now()-datetime.timedelta(days=365)).date()

        delta = datetime.timedelta(days=30)
        while d >= end_date:

            user_day_history = user_history.filter(date__startswith=d)

            try:
                views = len(user_day_history)

                average += views

                view_times.append({ 'label': d.strftime('%B'), 'value': views })
            except:
                view_times.append({ 'label': d.strftime('%B'), 'value': 0 })

            d -= delta

        return [view_times[::-1], average]

    
    ### This Will present the statistics about the database clicks
    def databaseHits(self, community):
     
        # Check what questionnaires are associated with the community
        # For now, assuming that there is only one questionnaire.
        questionnaire = community.questionnaires.all()[0]
        
        # Get all hitcounts. I know that this is a hard operations, but we will need to refactor 
        # This code in order to achieve a better scalability. 
        
        hitcounts = HitCount.objects.all()
        view_times = []
        average = 0 
        for hitcount in hitcounts:
            try:
                fingerprint = Fingerprint.objects.get(id=hitcount.object_pk)
                
                if fingerprint.questionnaire != questionnaire:
                    continue
                if fingerprint.hits > 50:
                    view_times.append({ 'label': fingerprint.fingerprint_hash, 'value': fingerprint.hits })
                average += fingerprint.hits 
            except:
                pass
            
        return [view_times[::-1], average]     
    
    def searchHits(self, community): 
        pass 
    
        



admin.site.register(Community, CommunityAdmin)
admin.site.register(CommunityUser, CommunityUserAdmin)
admin.site.register(CommunitiesFavorited, CommunitiesFavoritedAdmin)
admin.site.register(PluginPermission, CommunityPermissionAdmin)
admin.site.register(CommunityDatabasePermission, CommunityDatabasePermissionAdmin)
admin.site.register(CommunityGroup, CommunityGroupAdmin)
admin.site.register(CommunityFields, CommunityFieldsAdmin)
admin.site.register(ExternalCommunity, ExternalCommunityAdmin)


# Register community statistics 
admin.site.register_view('community_statistics', 
                            view=login_required(staff_member_required(CommunityStatistics.as_view())))


