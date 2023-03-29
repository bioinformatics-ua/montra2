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
import userena.views
from django.conf import settings
from django.contrib.auth import get_user_model, logout, views as auth_views
from django.shortcuts import get_object_or_404, redirect
from userena.decorators import secure_required

from community.models import Community
from .forms import EditProfileFormExtra


# Prevent access to edit by not logged in users
@secure_required
def profile_edit(request,
                 edit_profile_form=EditProfileFormExtra,
                 template_name='userena/profile_form.html',
                 success_url=settings.BASE_URL,
                 extra_context=None, **kwargs):

    if request.user.is_authenticated():

        comm = None
        if settings.SINGLE_COMMUNITY:
            comm = Community.objects.all()[:1].get()

        username = request.user.username
        user = get_object_or_404(get_user_model(),
                                 username__iexact=username)

        profile = user.emif_profile

        user_initial = {'first_name': user.first_name,
                        'last_name': user.last_name}

        form = edit_profile_form(instance=profile, initial=user_initial)

        if request.method == 'POST':
            form = edit_profile_form(request.POST, request.FILES, instance=profile,
                                     initial=user_initial)

            if form.is_valid():
                profile = form.save()
                return redirect(success_url)

        if not extra_context:
            extra_context = dict()
            extra_context['form'] = form
            extra_context['profile'] = profile
            extra_context['request'] = request
            extra_context['activemenu'] = 'profile'

            if comm:
                extra_context['comm'] = comm

        if request.method == "GET":
            # If the prm=true GET argument is provided set profile_required_middleware=True
            #  so the "Change password" link is not rendered
            extra_context["profile_required_middleware"] = request.GET.get("prm") == "true"

        return userena.views.ExtraContextTemplateView.as_view(template_name=template_name,
            extra_context=extra_context)(request)

    return userena.views.signup(request, **kwargs)

# def profile_edit(request, **kwargs):
#     if request.user.is_authenticated():
#         extra_content = dict()
#         extra_content['request'] = request
#         return userena.views.profile_edit(request, username=request.user.username, extra_content=extra_content, **kwargs)

#     return userena.views.signup(request, **kwargs)

# Prevent access to signup/signin pages by logged in users
def signup(request, **kwargs):
    if request.user.is_authenticated():
        return redirect(settings.BASE_URL)

    return userena.views.signup(request, **kwargs)


def signin(request, **kwargs):
    if request.user.is_authenticated():
        return redirect(settings.BASE_URL)

    return userena.views.signin(request, **kwargs)

#force logout function on password reset
def wrapped_password_reset_confirm(request, **kwargs):
    logout(request)
    
    return auth_views.password_reset_confirm(request, **kwargs)
