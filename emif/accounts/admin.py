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

import datetime

from django import forms
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Max, Min
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View
from guardian.admin import GuardedModelAdmin
from userena.admin import UserenaAdmin
from userena.models import UserenaSignup
from userena.utils import get_profile_model

from accounts.models import EmifProfile, NavigationHistory, Profile
from accounts.models import RestrictedGroup, RestrictedUserDbs, TermsConditions
from fingerprint.models import Fingerprint


class TermsConditionsAdmin(admin.ModelAdmin):
    list_display = [ 'name', 'enabled', 'created_date', 'last_updated_on']

class NavigationAdmin(admin.ModelAdmin):
    list_display = ['user', 'path', 'date']
    search_fields = ['user__username','user__email','path']
    list_filter = ['user']

def name(obj):
    return "%s" % (obj.findName())
name.short_description = 'Name'

class RestrictedForm(forms.ModelForm):
    def __findName(self, hash):
        try:
            fn = Fingerprint.objects.get(fingerprint_hash=hash)

            return (fn.removed, fn.findName())

        except Fingerprint.DoesNotExist:
            return (False, hash)
    def __init__(self, *args, **kwargs):
        # initalize form
        super(RestrictedForm, self).__init__(*args, **kwargs)

        # rebuild choices
        w = self.fields['fingerprint'].widget
        choices = []
        for key, value in w.choices:
            (removed, name) = self.__findName(value)
            if not removed:
                choices.append((key, name))

        w.choices = sorted(choices, key=lambda x: x[1])

        z = self.fields['user'].widget

        z.choices = sorted(z.choices, key=lambda x:x[1])

class RestrictedFormGroup(forms.ModelForm):
    def __findName(self, hash):
        try:
            fn = Fingerprint.objects.get(fingerprint_hash=hash)

            return (fn.removed, fn.findName(), fn.id)

        except Fingerprint.DoesNotExist:
            return (False, hash)
    def __init__(self, *args, **kwargs):
        # initalize form
        super(RestrictedFormGroup, self).__init__(*args, **kwargs)

        # rebuild choices
        w = self.fields['fingerprints'].widget
        choices = []
        for key, value in w.choices:
            (removed, name, fnid) = self.__findName(value)
            if not removed:
                choices.append((fnid, name))

        w.choices = sorted(choices, key=lambda x: x[1])

class NavigationRestricted(admin.ModelAdmin):
    form = RestrictedForm
    list_display = ['user', name]
    search_fields = ['user']
    list_filter = ['user']

def Name(self):
    return self.group.name

class NavigationRestrictedGroup(admin.ModelAdmin):
    form = RestrictedFormGroup
    list_display = [Name]
    #search_fields = ['user']
    #list_filter = ['user']


class ChoiceForm(forms.Form):
    user = forms.ModelChoiceField(User.objects.all())

class UserStatistics(View):
    template_name = 'admin/user_statistics.html'

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
        user = request.POST.get('user', -1)

        if(user == ""):
            return self.get(request)

        form = ChoiceForm(initial = {'user': user})

        user_history = NavigationHistory.objects.filter(user=user)

        most_viewed = user_history.values('path').annotate(number_viewed=Count('path')).order_by('-number_viewed')[:15]

        session_time, average_time = self.getSessionTimes(user_history)

        views_time, average_views = self.getViewTimes(user_history)

        return render(request, self.template_name, {'choice': form, 'global': False,
                                                    'most_viewed': most_viewed,
                                                    'session_time': session_time,
                                                    'session_average': average_time,
                                                    'views_time': views_time,
                                                    'views_average': average_views
                                                    })

    def getSessionTimes(self, user_history):

        session_times = []
        average = 0
        d = timezone.now().date()
        end_date = (timezone.now()-datetime.timedelta(days=30)).date()

        delta = datetime.timedelta(days=1)
        while d >= end_date:

            user_day_history = user_history.filter(date__startswith=d)

            min = user_day_history.aggregate(Min('date'))['date__min']
            max = user_day_history.aggregate(Max('date'))['date__max']

            try:
                session = (max-min).total_seconds() / 3600

                average += session

                session_times.append({ 'label': d, 'value': session })
            except:
                session_times.append({ 'label': d, 'value': 0 })

            d -= delta

        return [session_times[::-1], average/30]

    def getViewTimes(self, user_history):

        view_times = []
        average = 0
        d = timezone.now().date()
        end_date = (timezone.now()-datetime.timedelta(days=30)).date()

        delta = datetime.timedelta(days=1)
        while d >= end_date:

            user_day_history = user_history.filter(date__startswith=d)

            try:
                views = len(user_day_history)

                average += views

                view_times.append({ 'label': d, 'value': views })
            except:
                view_times.append({ 'label': d, 'value': 0 })

            d -= delta

        return [view_times[::-1], average/30]

admin.site.register_view('user_statistics', view=login_required(staff_member_required(UserStatistics.as_view())))

admin.site.register(Profile)

admin.site.register(NavigationHistory, NavigationAdmin)
admin.site.register(RestrictedUserDbs, NavigationRestricted)

admin.site.register(RestrictedGroup, NavigationRestrictedGroup)
admin.site.register(TermsConditions, TermsConditionsAdmin)


class UserAdminForm(UserenaAdmin):

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        (_('Personal info'), {'fields': ('email',)}),
    )

    def response_add(self, request, obj, post_url_continue=None):
        # Use the new successfully created user to create a EMIF profile and set
        #  necessary permissions
        UserenaSignup.objects.create_empty_profile(obj)
        return super(UserAdminForm, self).response_add(request, obj, post_url_continue)


admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UserAdminForm)


class EmifProfileAdmin(GuardedModelAdmin):

    def has_add_permission(self, request):
        return False


admin.site.register(get_profile_model(), EmifProfileAdmin)
