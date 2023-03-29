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

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Max
from django_resized import ResizedImageField
from django.core.validators import MaxValueValidator, MinValueValidator

from fingerprint.models import Fingerprint


def iconHash(instance, filename):
    ''' Callable to be called by the ImageField, this renames the file to the generic hash
        so we avoid collisions
    '''
    return '.{0}icons/{1}'.format(settings.MEDIA_URL, instance.slug)

# There are three types of plugins:
class Plugin(models.Model):
    GLOBAL      = 0
    DATABASE    = 1
    THIRD_PARTY = 2
    FULL_FLEDGED= 3
    COMMUNITY   = 4

    TYPES = [
                (GLOBAL,        'Global plugin, for the main dashboard'),
                (DATABASE,      'Database related plugin, for the database view'),
                (FULL_FLEDGED,  'Full-fledged application widget'),
                (THIRD_PARTY,   'Third party full-fledged applications'),
            ]

    # There are three ways of viewing plugins
    HTML_IFRAME = 0
    TP_IFRAME = 1
    EXT_LINK = 2
    
    PLUGIN_VIEW_TYPE = [
        (HTML_IFRAME, 'Use the Default IFrame from HTML'),
        (TP_IFRAME, 'Use the Third Party IFrame'),
        (EXT_LINK, 'Use as Link to Webpage')
    ]

    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)
    type = models.IntegerField(choices=TYPES, default=GLOBAL)
    owner= models.ForeignKey(User)
    icon = ResizedImageField(size=[200, 200], upload_to=iconHash, null=True, blank=True)
    create_date     = models.DateTimeField(auto_now_add=True)
    latest_update   = models.DateTimeField(auto_now=True)

    removed = models.BooleanField(default=False)

    plugin_index = models.IntegerField(default=1000, validators=[MinValueValidator(0), MaxValueValidator(999)])
    plugin_view = models.IntegerField(choices=PLUGIN_VIEW_TYPE, default=0)

    plugin_group = models.CharField(max_length=100, default="")
    plugin_group_index = models.IntegerField(default=1000, validators=[MinValueValidator(0), MaxValueValidator(999)])

    def create_date_repr(self):
        return self.create_date.strftime("%Y-%m-%d %H:%M:%S")

    def latest_update_repr(self):
        return self.latest_update.strftime("%Y-%m-%d %H:%M:%S")

    def type_repr(self):
        try:
            return dict(self.TYPES)[self.type]
        except KeyError:
            return "TYPE ERROR"

    @staticmethod
    def __generateSlug(name):
        return os.urandom(16).encode('hex');

    @staticmethod
    def create(name, type, owner, icon, group, view_type, pl_index, pg_index):
        slug = Plugin.__generateSlug(name)
        if(icon != None):
            p = Plugin(name=name, type=type, slug=slug, owner=owner, icon=icon, plugin_group=group, plugin_view=view_type, plugin_index=pl_index, plugin_group_index=pg_index)
        else:
            p = Plugin(name=name, type=type, slug=slug, owner=owner, plugin_group=group, plugin_view=view_type, plugin_index=pl_index, plugin_group_index=pg_index)
        p.save()

        if group:
            for same_group_plugin in Plugin.objects.filter(plugin_group=group).exclude(id=p.id):
                same_group_plugin.plugin_group_index = pg_index
                same_group_plugin.save()

        return p

    @staticmethod
    def update(slug, name, type, owner, icon, remove_icon, group, view_type, pl_index, pg_index):

        try:
            p = Plugin.objects.get(slug=slug)

        except Plugin.DoesNotExist:
            pass
        else:
            p.name = name
            p.type = type
            p.owner = owner
            p.plugin_group = group
            p.plugin_view = view_type
            p.plugin_index = pl_index
            p.plugin_group_index = pg_index

            if remove_icon:
                p.icon = None
            elif icon is not None:
                p.icon = icon

            p.save()

            if p.plugin_group:
                for same_group_plugin in Plugin.objects.filter(plugin_group=p.plugin_group).exclude(id=p.id):
                    same_group_plugin.plugin_group_index = pg_index
                    same_group_plugin.save()

            return p

        return None

    @staticmethod
    def all(owner=None, type=None, type_in=None):
        tmp = Plugin.objects.filter(removed = False)

        if owner != None:
            tmp = tmp.filter(owner=owner)

        if type != None:
            tmp = tmp.filter(type=type)

        if type_in != None:
            tmp = tmp.filter(type__in=type)

        return tmp

    # gets the file from the filesystem
    def getLatest(self):
        try:
            return self.versions().filter(approved=True)[:1][0]
        except PluginVersion.DoesNotExist:
            return None
    
    def getLatestPath(self):
        try:
            return self.versions().filter(approved=True)[0].path
        except PluginVersion.DoesNotExist:
            return ""

    def versions(self):
        return PluginVersion.all(plugin=self)

    @staticmethod
    def remove(slug):
        try:
            plugin = Plugin.objects.get(slug=slug)
        except Plugin.DoesNotExist:
            print "-- Error: Retrieving plugin"
            return False

        plugin.removed = True
        plugin.save()

        plugin.communityplugins_set.delete()

        return True


    def __str__(self):
        if self.name != None:
            return self.name

        return Undefined

    class Meta:
        ordering = ['id']

class PluginVersion(models.Model):
    plugin      = models.ForeignKey(Plugin)
    is_remote   = models.BooleanField(default=False)
    path        = models.TextField()
    version     = models.IntegerField()

    approved    = models.BooleanField(default=False)
    submitted   = models.BooleanField(default=False)
    submitted_desc = models.TextField(null=True, blank=True)
    create_date     = models.DateTimeField(auto_now_add=True)
    latest_update   = models.DateTimeField(auto_now=True)

    removed     = models.BooleanField(default=False)

    @staticmethod
    def all(plugin=None, approved=None):
        tmp = PluginVersion.objects.filter(removed=False, plugin__removed=False)

        if plugin != None:
            tmp = tmp.filter(plugin=plugin)

        if approved != None:
            tmp = tmp.filter(approved=True)

        return tmp

    @staticmethod
    def create(plugin_hash, version, is_remote, data):
        pv = None
        p = Plugin.objects.get(slug=plugin_hash)

        pv = PluginVersion(plugin = p, is_remote = is_remote,
            path = data, version = version)

        pv.save()

        return pv

    @staticmethod
    def submit(plugin_hash, version, desc):
        from developer.tasks import sendCommitEmails

        pv  = None
        p   = Plugin.objects.get(slug=plugin_hash)

        try:
            pv = PluginVersion.all(plugin=p).get(version=version)

            pv.submitted = True
            pv.approved = False
            pv.submitted_desc = desc

            sendCommitEmails.apply_async([p, pv])

            pv.save()

        except PluginVersion.DoesNotExist:
            pass

        return pv

    @staticmethod
    def update(plugin_hash, version_old, version_new, is_remote, data):
        pv = None
        p = Plugin.objects.get(slug=plugin_hash)
        try:
            pv = PluginVersion.all(plugin=p).get(version=version_old)

            pv.version = version_new
            pv.is_remote = is_remote
            pv.path = data

            pv.submitted = False
            pv.approved = False

            pv.save()

        except PluginVersion.DoesNotExist:
            pass

        return pv

    def __str__(self):
        return '%s : v.%r' % (self.plugin.name, self.version)

    def create_date_repr(self):
        return self.create_date.strftime("%Y-%m-%d %H:%M:%S")

    def latest_update_repr(self):
        return self.latest_update.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def all_valid(type=None):
        all = None

        all = PluginVersion.all(approved=True).order_by('plugin__id', '-version').distinct('plugin__id')

        if type != None:
            all = all.filter(plugin__type=type)

        return all


    class Meta:
        ordering = ['-version']
        verbose_name_plural = "Plugin versions waiting for approval"

class PluginFingeprint(models.Model):
    plugin = models.ForeignKey(Plugin)
    fingerprint = models.ForeignKey(Fingerprint)
    empty = models.BooleanField(default=True)

    @staticmethod
    def create(plugin_hash, fingerprint_hash, boolean):
        try:
            fp = Fingerprint.objects.valid(include_drafts=True).get(fingerprint_hash=fingerprint_hash)
            p = Plugin.objects.get(slug=plugin_hash)
        except Fingerprint.DoesNotExist:
            pass

        pf = None
        
        if boolean == 'false':
            boolean = False
        else:
            boolean = True
        
        if not PluginFingeprint.exists(plugin_hash, fingerprint_hash):
            pf = PluginFingeprint(plugin=p,fingerprint=fp,empty=boolean)
            pf.save()
        else:
            pf = PluginFingeprint.objects.get(plugin=p,fingerprint=fp)
            pf.empty = boolean
            pf.save()
            
        return pf
    
    @staticmethod
    def exists(plugin_hash, fingerprint_hash):
        try:
            fp = Fingerprint.objects.valid(include_drafts=True).get(fingerprint_hash=fingerprint_hash)
        except Fingerprint.DoesNotExist:
            return False
        
        try:
            p = Plugin.objects.get(slug=plugin_hash)
        except Plugin.DoesNotExist:
            return False

        try:
            PluginFingeprint.objects.get(plugin=p,fingerprint=fp)
            return True
        except PluginFingeprint.DoesNotExist:
            return False
    
    def __str__(self):
        return '(Plugin:%s , Fingerprint:%s) %s' % (self.plugin.name, self.fingerprint.fingerprint_hash,self.empty)

# Upload dependencies
class VersionDep(models.Model):
    pluginversion = models.ForeignKey(PluginVersion)
    created_date = models.DateTimeField(auto_now_add=True)
    latest_date = models.DateTimeField(auto_now=True)
    revision = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    filename = models.CharField(max_length=255)
    size = models.FloatField(default=0)
    removed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-latest_date']

    @staticmethod
    def all(version=None):
        tmp = VersionDep.objects.filter(removed=False)

        if version != None:
            tmp = tmp.filter(pluginversion=version)

        return tmp

    @staticmethod
    def unique(version=None):
        version_deps = VersionDep.all(version=version)

        deps = version_deps.values('filename').annotate(latest=Max('latest_date'))
        uniquedeps = []
        for file in deps:
            uniquedeps.append(version_deps.get(filename = file['filename'], latest_date = file['latest']))

        return uniquedeps
