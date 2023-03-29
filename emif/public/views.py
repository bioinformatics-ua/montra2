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
from constance import config
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render

from community.utils import getComm
from fingerprint.views import document_form_view_comm
from .models import PublicFingerprintShare
from .services import createFingerprintShare, deleteFingerprintShare, shouldDelete


def fingerprint_list(request, community=None):
    if not config.privateLinksMenu or not request.user.is_authenticated():
        raise Http404

    comm = getComm(community, request.user)
    if isinstance(comm, HttpResponseRedirect):
        return comm

    alink = request.session.get('created_public_link')
    dlink = request.session.get('deleted_public_link')
    try:
        del request.session['created_public_link']
        del request.session['deleted_public_link']
    except:
        pass

    request.session.modified = True

    comm_dbs = comm.getDatabases()
    comm_dbs_names = []

    own_dbs      = comm_dbs.filter(owner=request.user)
    shared_dbs   = comm_dbs.filter(shared=request.user)

    links_query  = PublicFingerprintShare.objects.filter(user=request.user, fingerprint__in = comm_dbs)

    links = []
    linkedfingerprints = []
    # This is a bother, must find names since they are not readily available anywhere... I reiterate i think the name
    # should be linked somehow to the fingerprint object directly...
    for link in links_query:
        remove = shouldDelete(link)

        if remove:
            link.delete()
            continue

        this_fingerprint = link.fingerprint

        linkedfingerprints.append(this_fingerprint.id)

        name = this_fingerprint.findName()

        links.append({'name': name, 'share': link})

    intersection = own_dbs | shared_dbs
    #intersection_clean = intersection.filter(~Q(id__in=linkedfingerprints))

    intersection_wnames = []

    for db in comm_dbs:
        comm_dbs_names.append({'name':db.findName(), 'fingerprint':db})

    for o in intersection:
        name = o.findName()

        intersection_wnames.append({'name': name, 'fingerprint': o})

    return render(request, "fingerprints.html", {'request': request, 'links': links, 'create_public': True,
        'activemenu': 'databases', 'activesubmenu': 'private', 'comm': comm, "comm_db_names": comm_dbs_names,
        'own_dbs': intersection_wnames, 'hide_add': True, 'breadcrumb': True, 'added': alink, 'deleted': dlink})


def fingerprint(request, community, fingerprintshare_id):
    if not config.privateLinksMenu:
        raise Http404

    fingerprintshare = get_object_or_404(PublicFingerprintShare, hash=fingerprintshare_id)

    remove = shouldDelete(fingerprintshare)

    if remove:
        fingerprintshare.delete()
        raise Http404

    fingerprintshare.remaining_views = fingerprintshare.remaining_views - 1
    fingerprintshare.save()

    return document_form_view_comm(request, community, fingerprintshare.fingerprint.fingerprint_hash, 1, readOnly=True, public_key=fingerprintshare, force=True)


def fingerprint_create(request, fingerprint_id, community=None):
    if not config.privateLinksMenu or not request.user.is_authenticated():
        raise Http404

    createFingerprintShare(fingerprint_id, request.user)

    request.session['created_public_link'] = True
    request.session['deleted_public_link'] = False
    return redirect('public.views.fingerprint_list', community=community)


def fingerprint_delete(request, share_id, community=None):
    if not config.privateLinksMenu or not request.user.is_authenticated():
        raise Http404

    deleteFingerprintShare(share_id)

    request.session['deleted_public_link'] = True
    request.session['created_public_link'] = False
    return redirect('public.views.fingerprint_list', community=community)
