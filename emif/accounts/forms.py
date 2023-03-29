# -*- coding: utf-8 -*-
# Copyright (C) 2022 Universidade de Aveiro, DETI/IEETA, Bioinformatics Group - http://bioinformatics.ua.pt/
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
import random
from abc import abstractmethod
from hashlib import sha1 as sha_constructor

import django_countries
from constance import config
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from guardian.shortcuts import assign_perm
from userena.forms import EditProfileForm, SignupForm
from userena.managers import ASSIGNED_PERMISSIONS
from userena.utils import get_profile_model, get_user_profile

from community.models import Community, CommunityJoinForm, CommunityJoinFormReply, CommunityUser
from questionnaire.models import Questionnaire
from security.recaptcha import Recaptcha
from terms.models import TermsAccept
from .models import Profile, TermsConditions

options = (
    (5, '5'),
    (10, '10'),
    (25, '25'),
    (50, '50'),
    (-1, 'All'),
)
types = (
    ('answers', 'Search on answers'),
    ('questions', 'Search on questions'),
    ('all', 'Search answers and questions')
)


class JoinForm(SignupForm):
    """
    A form to add extra fields to the signup form.
    """

    first_name = forms.CharField(label=_('First name'), max_length=30, required=True)
    last_name = forms.CharField(label=_('Last name'), max_length=30, required=True)
    country = forms.ChoiceField(
        [(None, "---")] + list(django_countries.countries),
        required=True,
    )
    organization = forms.CharField(label=_('Organization'), max_length=255, required=True)

    '''profiles = forms.ModelMultipleChoiceField(label=_('I am a (select all that apply):'),
                                                required=True,
                                                queryset=Profile.objects.all(),
                                                widget=forms.CheckboxSelectMultiple())


    interests = forms.ModelMultipleChoiceField(label=_('I am interested in (select all that apply):'),
                                                required=True,
                                                queryset=Questionnaire.objects.filter(disable='False'),
                                                widget=forms.CheckboxSelectMultiple())'''

    '''paginator = forms.ChoiceField(label=_('Select default value for paginations:'),
                                        choices = options
                                    )
    '''

    '''search_type = forms.ChoiceField(label=_('Select default type of search:'),
                                        choices = types
                                    )
    '''

    mail_news = forms.BooleanField(
        label=_('Receive weekly newsletter e-mail with database updates ?'),
        required=False,
        initial=False,
    )
    mail_not = forms.BooleanField(
        label=_('Receive all notifications over e-mail ?'),
        required=False,
        initial=False,
    )

    def __init__(self, *args, **kw):
        super(JoinForm, self).__init__(*args, **kw)

        self._pre_init(args)

        # put regular fields at the top
        if Profile.objects.all().count() and Questionnaire.objects.all().count():
            self.fields.keyOrder = ['first_name', 'last_name', 'country', 'organization', 'email', 'password1', 'password2', 'mail_news', 'mail_not']
        elif Profile.objects.all().count():
            self.fields.keyOrder = ['first_name', 'last_name', 'country', 'organization', 'email', 'password1', 'password2', 'mail_news', 'mail_not']
        elif Questionnaire.objects.all().count():
            self.fields.keyOrder = ['first_name', 'last_name', 'country', 'organization', 'email', 'password1', 'password2', 'mail_news', 'mail_not']
        else:
            self.fields.keyOrder = ['first_name', 'last_name', 'country', 'organization', 'email', 'password1', 'password2', 'mail_news', 'mail_not']

        if not config.newsletter:
            del self.fields["mail_news"]
            self.fields.keyOrder.remove("mail_news")

        # add join form fields on single community
        if settings.SINGLE_COMMUNITY:
            try:
                if Community.objects.count() > 1:
                    comm = Community.objects.all()[0]
                else:
                    comm = Community.objects.get()
            except Community.DoesNotExist:
                pass
            else:
                self.join_form = CommunityJoinForm.objects.filter(community=comm)

                previous_len = len(self.fields)

                for question in self.join_form:
                    self.fields[question.question_text] = forms.CharField(required=question.required)

                fields = self.fields.keys()

                self.order_fields(
                    fields[:previous_len - 2] + \
                    fields[previous_len:] + \
                    fields[:previous_len - 2:previous_len]
                )

        # Get term and conditions
        # We are prioritizing installation level terms and conditions over community level, for
        #  single community installations with a public community
        enabled_terms = TermsConditions.objects.filter(enabled=True)
        if enabled_terms.exists():
            self.availableTerms = True
            self.terms = enabled_terms[0]
        else:
            self.availableTerms = False

            if settings.SINGLE_COMMUNITY:
                if Community.objects.count() > 1:
                    comm = Community.objects.all()[0]
                else:
                    comm = Community.objects.get()

                if comm.membership == comm.MEMBERSHIP_PUBLIC and comm.disclaimer:
                    self.availableTerms = True
                    self.terms = TermsConditions(name="Terms and Conditions", description=comm.disclaimer)

        # set recaptcha key
        self.RECAPTCH_PUBLIC_KEY = settings.RECAPTCH_PUBLIC_KEY

    @abstractmethod
    def _pre_init(self, args):
        pass

    def save(self, *args):
        """
        Override the save method to save additional fields to the user profile
        and override username with email.
        """
        if config.recaptcha_verification:
            recaptcha = Recaptcha(settings.BASE_URL, settings.RECAPTCH_PUBLIC_KEY, settings.RECAPTCH_PRIVATE_KEY)
            if not recaptcha.verify(self._get_recaptcha_response()):
                return HttpResponse('Invalid Recaptcha. Please try again.')

        # Use trimmed email as username
        username = self.cleaned_data['email'][:30]
        try:
            get_user_model().objects.get(username__iexact=username)
        except get_user_model().DoesNotExist:
            pass
        else:  # Fallback to randomly assigned username
            while True:
                username = sha_constructor(str(random.random())).hexdigest()[:5]
                try:
                    get_user_model().objects.get(username__iexact=username)
                except get_user_model().DoesNotExist:
                    break

        new_user = self._create_user_obj(username, args)

        # save user data
        new_user.first_name = self.cleaned_data['first_name']
        new_user.last_name = self.cleaned_data['last_name']
        new_user.save()
        user_profile = new_user.emif_profile
        user_profile.country = self.cleaned_data['country']
        user_profile.organization = self.cleaned_data['organization']
        user_profile.paginator = int(self.cleaned_data.get('paginator', 5))
        user_profile.search_type = self.cleaned_data.get('search_type', "all")
        if not config.newsletter:
            user_profile.mail_news = False
        else:
            user_profile.mail_news = self.cleaned_data.get('mail_news', True)
        user_profile.mail_not = self.cleaned_data.get('mail_not', False)
        user_profile.save()

        # add to community and parse join form answers on single community
        if settings.SINGLE_COMMUNITY:
            try:
                if Community.objects.count() > 1:
                    comm = Community.objects.all()[0]
                else:
                    comm = Community.objects.get()
            except Community.DoesNotExist:
                return
            else:
                # Add association on single community mode
                cu = CommunityUser.objects.create(community=comm, user=new_user, status=CommunityUser.DISABLED)

                for question in self.join_form:
                    if question.question_text in self.cleaned_data \
                            and self.cleaned_data[question.question_text] != self.fields[question.question_text].empty_value:
                        CommunityJoinFormReply.objects.create(
                            commuser=cu, join_form=question, reply_text=self.cleaned_data[question.question_text]
                        )

        terms_accept = TermsAccept(user=new_user)
        terms_accept.save()


        # Userena expects to get the new user from this form, so return the new
        # user.
        return new_user

    @abstractmethod
    def _get_recaptcha_response(self):
        pass

    @abstractmethod
    def _create_user_obj(self, username, save_args):
        pass


class SocialSignupFormExtra(JoinForm):

    def _pre_init(self, args):
        # Only when it is request.POST && to capture the capcha
        try:
            self.recaptcha_response = self.data['g-recaptcha-response']
        except:
            self.recaptcha_response = ''

    def _get_recaptcha_response(self):
        return self.recaptcha_response

    def _create_user_obj(self, username, save_args):
        """
        Update social user with userena data that is created during the signup process
        """
        social_user = save_args[0]

        social_user.username = username

        # All users have an empty profile
        profile_model = get_profile_model()
        try:
            new_profile = social_user.emif_profile

        except profile_model.DoesNotExist:
            new_profile = profile_model(user=social_user)
            new_profile.save()

        # Give permissions to view and change profile
        for perm in ASSIGNED_PERMISSIONS['profile']:
            assign_perm(perm[0], social_user, get_user_profile(user=social_user))

        # Give permissions to view and change itself
        for perm in ASSIGNED_PERMISSIONS['user']:
            assign_perm(perm[0], social_user, social_user)

        return social_user


class SignupFormExtra(JoinForm):

    def _pre_init(self, args):
        del self.fields['username']

        # Only when it is request.POST && to capture the capcha
        try:
            self.requestInfo = args[0]
        except:
            pass

    def _get_recaptcha_response(self):
        return self.requestInfo.get('g-recaptcha-response', '')

    def _create_user_obj(self, username, save_args):
        self.cleaned_data['username'] = username

        # First save the parent form and get the user.
        return super(JoinForm, self).save()


class EditProfileFormExtra(EditProfileForm):

    '''profiles = forms.ModelMultipleChoiceField(label=_('I am a (select all that apply):'),
                                                required=True,
                                                queryset=Profile.objects.all(),
                                                widget=forms.CheckboxSelectMultiple())

    interests = forms.ModelMultipleChoiceField(label=_('I am interested in (select all that apply):'),
                                                required=True,
                                                queryset=Questionnaire.objects.filter(disable='False'),
                                                widget=forms.CheckboxSelectMultiple())'''

    paginator = forms.ChoiceField(label=_('Select default value for paginations:'),
                                  choices = options
                                  )

    search_type = forms.ChoiceField(label=_('Select default type of search:'),
                                    choices = types
                                    )

    mail_news = forms.BooleanField(label=_('Receive weekly newsletter e-mail with database updates ?'),
                                   required=False,

                                   )

    mail_not = forms.BooleanField(label=_('Receive all notifications over e-mail ?'),
                                  required=False,
                                  )

    def __init__(self, *args, **kw):
        super(EditProfileFormExtra, self).__init__(*args, **kw)
        del self.fields['mugshot']
        del self.fields['privacy']
        del self.fields['restricted']

        if Profile.objects.all().count() and Questionnaire.objects.all().count():
            self.fields.keyOrder = ['username', 'first_name', 'last_name', 'country', 'organization', 'paginator', 'search_type', 'mail_news', 'mail_not']
        elif Profile.objects.all().count():
            self.fields.keyOrder = ['username', 'first_name', 'last_name', 'country', 'organization', 'paginator', 'search_type', 'mail_news', 'mail_not']
        elif Questionnaire.objects.all().count():
            self.fields.keyOrder = ['username', 'first_name', 'last_name', 'country', 'organization', 'paginator', 'search_type', 'mail_news', 'mail_not']
        else:
            self.fields.keyOrder = ['username', 'first_name', 'last_name', 'country', 'organization', 'paginator', 'search_type']

        if not config.newsletter:
            del self.fields["mail_news"]
            try:
                self.fields.keyOrder.remove("mail_news")
            except ValueError:
                pass

    def save(self, force_insert=False, force_update=False, commit=True):
        profile = super(EditProfileFormExtra, self).save(force_insert, force_update, commit)

        if not config.newsletter:
            profile.mail_news = False  # force false on newsletter feature deactivated
            profile.save()
