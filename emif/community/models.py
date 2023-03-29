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
import logging
import uuid

from constance import config
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db import transaction
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template import loader
from django_resized import ResizedImageField

from developer.models import Plugin
from emif.tasks import send_custom_mail
from fingerprint.models import Fingerprint
from fingerprint.models import Fingerprint
from public.models import PublicFingerprintShare
from questionnaire.models import Question
from questionnaire.models import Questionnaire
from searchengine.search_indexes import CoreEngine
from tag.models import Tag


def iconHash(instance, filename):
    ''' Callable to be called by the ImageField, this renames the file to the generic hash
        so we avoid collisions
    '''
    return 'icons/community/{0}.jpg'.format(instance.slug)

def iconThumbnail(instance, filename):
    ''' Callable to be called by the ImageField, this renames the file to the generic hash
        so we avoid collisions
    '''
    return 'thumbnails/community/{0}.jpg'.format(instance.slug)


class Community(models.Model):
    MEMBERSHIP_OPEN = "open"
    MEMBERSHIP_PUBLIC = "public"
    MEMBERSHIP_MODERATED = "moderated"
    MEMBERSHIP_INVITATION = "invitation"

    HEADER_DISPLAY_NONE_TYPE = "none"
    HEADER_DISPLAY_COMM_TYPE = "comm"
    HEADER_DISPLAY_QUES_TYPE = "ques"
    HEADER_DISPLAY_BOTH_TYPE = "both"

    QUESTIONNAIRES_VIEW_LIST = "list"
    QUESTIONNAIRES_VIEW_CARD = "card"

    MEMBERSHIP_TYPES = (
        (MEMBERSHIP_OPEN, 'open'),
        (MEMBERSHIP_PUBLIC, 'public'),
        (MEMBERSHIP_MODERATED, 'moderated'),
        (MEMBERSHIP_INVITATION, 'invitation'),
    )
    DEFAULT_MEMBERSHIP='moderated'

    HEADER_DISPLAY_TYPES = (
        (HEADER_DISPLAY_NONE_TYPE, 'Do not display'),
        (HEADER_DISPLAY_COMM_TYPE, 'Community logo'),
        (HEADER_DISPLAY_QUES_TYPE, 'Questionnaire logos'),
        (HEADER_DISPLAY_BOTH_TYPE, 'Community and questionnaire logos'),
    )
    DEFAULT_HEADER_DISPLAY = HEADER_DISPLAY_NONE_TYPE

    QUESTIONNAIRES_VIEW_TYPES = (
        (QUESTIONNAIRES_VIEW_LIST, 'List view'),
        (QUESTIONNAIRES_VIEW_CARD, 'Card view'),
    )

    DEFAULT_QUESTIONNAIRES_VIEW = QUESTIONNAIRES_VIEW_LIST

    owners          = models.ManyToManyField(User, blank=True)
    invisible_owners= models.ManyToManyField(User, blank=True, related_name='invisible')
    name            = models.CharField(max_length=100)
    description     = models.CharField(max_length=5000, null=True, blank=True)
    disclaimer      = models.CharField(max_length=5000, null=True, blank=True)
    short_desc      = models.CharField(max_length=200)
    public          = models.BooleanField(default=False)
    auto_accept     = models.BooleanField(default=False)
    membership      = models.CharField(max_length=100, choices=MEMBERSHIP_TYPES, default=DEFAULT_MEMBERSHIP)
    slug            = models.CharField(max_length=50, unique=True)
    icon            = ResizedImageField(size=[500, 200], upload_to=iconHash, null=True, blank=True)
    thumbnail       = ResizedImageField(size=[500, 200], upload_to=iconThumbnail, null=True, blank=True)
    sortid          = models.IntegerField(default=0)
    questionnaires  = models.ManyToManyField(Questionnaire, blank=True)

    # this is really not cool, pop char and documents should be migrated to the plugin structure,like other tabs
    show_popchar    = models.BooleanField(default=True)
    show_docs       = models.BooleanField(default=True)

    header_display  = models.CharField(max_length=4, choices=HEADER_DISPLAY_TYPES, default=DEFAULT_HEADER_DISPLAY)
    questionnaires_display  = models.CharField(max_length=4, choices=QUESTIONNAIRES_VIEW_TYPES, default=DEFAULT_QUESTIONNAIRES_VIEW)

    popchar_sortid  = models.IntegerField(default=0)
    docs_sortid     = models.IntegerField(default=0)
    db_sortid       = models.IntegerField(default=0)
    dblist_sortid   = models.IntegerField(default=0)

    plugins         = models.ManyToManyField(Plugin, through='CommunityPlugins')
    list_fields     = models.ManyToManyField(Question, through='CommunityFields')
    tags            = models.ManyToManyField(Tag, blank=True)
    query           = models.CharField(max_length=200, default="", blank=True)

    landpage_url = models.CharField(max_length=100, blank=True, default="")

    @transaction.atomic
    def set_tags(self, tags):
        self.tags.clear()

        for tag in tags:
            self.tags.add(tag)

    def get_permissions(self):
        try:
            return self.communitypermissions

        except CommunityPermissions.DoesNotExist:
            cp = CommunityPermissions(community=self)
            cp.save()
            return cp

        return None

    def getCount(self):
        qsts = self.questionnaires.all()
        return Fingerprint.objects.filter(questionnaire__in=qsts, removed=False, draft=False, community_id=self.id).count()

    # *********************
    def hasLocation(self):
        #print "*** has location ", 
        quest=self.questionnaires.all().values_list('slug', flat=True)
        #advancedquery, community, disable, fingerprint, id, name, qsets, questionnairewizard, questionset, redirect_url, slug
        location = False

        c = CoreEngine()
        query="*:*" 
        results = c.search_fingerprint(query, sort="", rows=100, start=0, fl='*,score', qop='AND')
        for r in results:
            try:
                # if this community questionaire is the same as the one in Solr and there is a location field then...
                if ( quest[0] == r['type_t'] ) :
                    #print "#ID#",r['id']
                    #print "#TYPE#",r['type_t']
                    #print "#LOC#",r['location_s']
                    if r['location_s']:
                        location = True
            except:
                #print("no data...")
                pass

        return location
    # *********************

    def getDatabases(self):
        qsts = self.questionnaires.all()

        return Fingerprint.objects.filter(questionnaire__in=qsts, removed=False, draft=False)

    def is_owner(self, user):
        is_owner = False
        #print ("*** A *** " ) 
        
        # Check normal owners
        try:
            self.owners.get(id=user.id)
            is_owner = True

            #fix: enable Community Manager if not enabled by default
            #print ("*** %s IS OWNER %s***" % (user, self))
            try:
                cu = CommunityUser.objects.get(community=self, user=user)
            except:
                print ("*** manager not a community user... fixing... *** " )
                try:
                    cu = CommunityUser(community=self, user=user, status=CommunityUser.ENABLED)
                    cu.save()
                    print ("*** Community Manager Enabled ***")
                except:
                    pass
            #--end

            return True
        except User.DoesNotExist:
            pass


        # check invisible_owners
        try:
            self.invisible_owners.get(id=user.id)
            is_owner = True
            return True
        except User.DoesNotExist:
            pass
        return is_owner


    def belongs(self, user):
        if self.public:
            return True

        if not user.is_authenticated():
            return None
            
        try:
            cu = CommunityUser.objects.get(community=self, user=user)

            if cu.status==CommunityUser.ENABLED or cu.status==CommunityUser.RESTRICTED:
                return cu

        except CommunityUser.DoesNotExist:
            return None

        return False

    def pending(self):
        return CommunityUser.objects.filter(community=self, status=CommunityUser.DISABLED)

    def getSolrSlugs(self):
        quests = self.questionnaires.all().values_list('slug', flat=True)
        if not quests:
            return None
        for quest in quests:
            tmp = ' OR type_t: '.join(quests)
        tmp = '(type_t:' + tmp + ')'
        return tmp

    def get_communityfields(self, questionnaire, view):

        if view:
            return self.communityfields_set.filter(questionnaire=questionnaire, view=view).order_by('sortid')
        else:
            return self.communityfields_set.filter(questionnaire=questionnaire).order_by('sortid')

    class Meta:
        verbose_name_plural = "Communities"
        ordering = ["sortid", "id"]

    def __unicode__(self):
        return self.name

    def getCommunityPlugins(self):
        return CommunityPlugins.objects.filter(community=self).filter(Q(plugin__type=Plugin.THIRD_PARTY) | Q(plugin__type=Plugin.FULL_FLEDGED))

    def getAllCommunityPlugins(self):
        """
        This method will save he community's plugins that are either THIRD_PARTY or FULL_FLEDGED in a list
        It returns them in a list containing the plugins in the order specified previously.

        Returns:
            A list containing all the community's plugins.
        """
        return CommunityPlugins.objects.filter(community=self)\
            .filter(Q(plugin__type=Plugin.THIRD_PARTY) | Q(plugin__type=Plugin.FULL_FLEDGED))


class CommunityPermissions(models.Model):
    community = models.OneToOneField(Community)
    export_dblist = models.BooleanField(default=True)
    export_fingerprint = models.BooleanField(default=True)
    export_datatable = models.BooleanField(default=True)

    def __unicode__(self):
        return 'CommunityPermissions - {Export Datatables: %r, Export Fingerprint: %r, Export Db lists: %r}' % (self.export_datatable, self.export_fingerprint, self.export_dblist)


class CommunitiesFavorited(models.Model):
    community = models.ForeignKey(Community)
    user = models.ForeignKey(User)


class CommunityUser(models.Model):
    DISABLED = 0
    ENABLED = 1
    RESTRICTED = 2
    BLOCKED = 3
    REJECTED = 4
    REMOVED = 5
    POSSIBLE_STATUS = (
        (DISABLED, 'Waiting approval in community'),
        (ENABLED, 'Enabled in community'),
        (RESTRICTED, 'Enabled, but with restricted access to certain databases'),
        (BLOCKED, 'Blocked by community owner'),

        # These below are not actual status. Logic is implemented to delete CommunityUser records once
        #  they enter these statuses.
        (REJECTED, 'Not accepted into the community'),
        (REMOVED, 'Removed from the community'),
    )
    community       = models.ForeignKey(Community)
    user            = models.ForeignKey(User, related_name="community_users")
    status          = models.PositiveSmallIntegerField(default=DISABLED, choices=POSSIBLE_STATUS)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("community", "user")

    def __unicode__(self):
        username = self.user.get_full_name()

        if not username:
            username = self.user.email

        return "%s - %s" % (username, self.community.name)


class CommunityActivationMessage(models.Model):
    """
    Used to keep a history of messages sent to community users
    """
    community = models.ForeignKey(Community)
    message = models.TextField()

    class Meta:
        unique_together = ("community", "message")


def randomHash():
    return uuid.uuid1().hex


class CommunityActivation(models.Model):
    community = models.ForeignKey(Community)
    user = models.ForeignKey(User)
    commuser = models.ForeignKey(CommunityUser, null=True, on_delete=models.SET_NULL)
    hash = models.CharField(max_length=32, default=randomHash)
    used = models.BooleanField(default=False)
    msg2user = models.ForeignKey(CommunityActivationMessage, null=True, blank=True, on_delete=models.SET_NULL)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True, null=True)

    def activate(self, next_status=CommunityUser.ENABLED, notify=True):
        if notify:
            send_custom_mail.delay(
                '{}: Accepted into {}'.format(settings.GLOBALS['BRAND'], self.community.name),
                loader.render_to_string(
                    "emails/granted_access.html",
                    {
                        "user_full_name": self.user.get_full_name(),
                        "community_name": self.community.name,
                        "BASE_URL": settings.BASE_URL,
                        "community_slug": self.community.slug,
                        "brand": settings.GLOBALS['BRAND'],
                    },
                ),
                settings.DEFAULT_FROM_EMAIL,
                [self.user.email],
            )

        self.commuser.status = next_status
        self.commuser.save()
        self.used = True
        self.save()

    def dontactivate(self, msg2user=None):
        send_custom_mail.delay(
            '{}: Access not granted to {}'.format(settings.GLOBALS['BRAND'], self.community.name),
            loader.render_to_string(
                "emails/not_accepted.html",
                {
                    "user_full_name": self.user.get_full_name(),
                    "community_name": self.community.name,
                    "brand": settings.GLOBALS['BRAND'],
                    "comm_manager_msg": msg2user,
                },
            ),
            settings.DEFAULT_FROM_EMAIL,
            [self.user.email],
        )

        self.commuser.delete()
        self.commuser = None
        self.used = True
        self.save()

    def block(self, msg2user=None):
        send_custom_mail.delay(
            '{}: You were blocked from community {}'.format(settings.GLOBALS['BRAND'], self.community.name),
            loader.render_to_string(
                "emails/blocked.html",
                {
                    "user_full_name": self.user.get_full_name(),
                    "community_name": self.community.name,
                    "brand": settings.GLOBALS['BRAND'],
                    "comm_manager_msg": msg2user,
                },
            ),
            settings.DEFAULT_FROM_EMAIL,
            [self.user.email],
        )

        self.commuser.status = CommunityUser.BLOCKED
        self.commuser.save()
        self.used = True
        self.save()


@receiver(post_save, sender=CommunityActivation)
def __notify_email(sender, instance, *args, **kwargs):
    #This method uses the post_save signal on Questionnaire to generate wizards to existing users
    if kwargs["created"]:
        cu = instance.commuser

        username = cu.user.get_full_name()

        if not username:
            username = cu.user.email

        if cu.community.membership == Community.MEMBERSHIP_PUBLIC:
            instance.activate(notify=False)
        else:
            manager_message = loader.render_to_string(
                "emails/join_request.html",
                {
                    "username": username,
                    "community_name": cu.community.name,
                    "user_email": cu.user.email,
                    "user_organization": cu.user.emif_profile.organization,
                    "user_country": cu.user.emif_profile.country,
                    "BASE_URL": settings.BASE_URL,
                    "activation_hash": instance.hash,
                    "brand": settings.GLOBALS['BRAND'],
                },
            )

            logging.debug("*** CommunityActivation EMAIL:\n %s\n***" % manager_message)

            send_custom_mail.delay(
                '{}: {} wants to join {}'.format(settings.GLOBALS['BRAND'], username, cu.community.name),
                manager_message,
                settings.DEFAULT_FROM_EMAIL,
                cu.community.owners.values_list('email', flat=True),
            )


class CommunityPlugins(models.Model):
    plugin = models.ForeignKey(Plugin)
    community = models.ForeignKey(Community)
    sortid = models.IntegerField(default=0)


class CommunityFields(models.Model):
    
    #view choices
    TABLE_VIEW = 'TB'
    LIST_VIEW = 'LT'
    CARD_VIEW = 'CD'
    VIEW_CHOICES = [
        (TABLE_VIEW, 'Table View'),
        (LIST_VIEW, 'List View'),
        (CARD_VIEW, 'Card View'),
    ]

    field = models.ForeignKey(Question, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, null=True)
    sortid = models.IntegerField(default=0)
    view = models.CharField(
        max_length=2,
        choices=VIEW_CHOICES,
        default=TABLE_VIEW,
        null=True
    )
    icon=models.CharField(
        max_length=50,
        default='',
        null=True
    )
    show_label = models.NullBooleanField(default=False)
    apply_formatting = models.BooleanField(default=True)
    section = models.IntegerField(default=0, null=True)


class CommunityExcludedExtraFields(models.Model):
    """
    Some views have a couple of hardcoded fields, such as
     the Last Update Column on the table view.
    By default all questionnaires of all communities have
     this field active. Each record on this model tell what
     hardcoded fields are excluded.
    """

    POSSIBLE_FIELDS = {
        CommunityFields.TABLE_VIEW: ("Last Update",),
        CommunityFields.LIST_VIEW: (),
        CommunityFields.CARD_VIEW: (),
    }

    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    view = models.CharField(max_length=2, choices=CommunityFields.VIEW_CHOICES)
    name = models.CharField(max_length=255)


class CommunityGroup(models.Model):
    """
    Groups to enforce permissions at a community level.

    There are already some pre-existing groups in any community which are created
    by the create_base_groups signal present on the signals.py file.
    However, this signal does not execute when loading communities through fixtures.
    This was done to avoid conflicts, which could lead to fixtures not being loaded.
    For that, when dealing with fixtures of this model, first load them, but then you
    should run `for comm in Community.objects.all(): comm.save()` so the mentioned signal
    is triggered and the missing pre-existing groups are created.
    """

    community = models.ForeignKey(Community, related_name="groups")
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, blank=True, null=True)
    removed = models.BooleanField(default=False)
    members = models.ManyToManyField(CommunityUser)

    DEFAULT_GROUP = "default"
    EDITORS_GROUP = "editors"
    STUDY_MANAGERS_GROUP = "study managers"
    API_GROUP = "API"
    DATABASE_OWNERS_GROUP = "database owners"
    PRE_EXISTING_GROUPS = {
        DEFAULT_GROUP: "default",
        EDITORS_GROUP: "editors",
        STUDY_MANAGERS_GROUP: "study managers",
        API_GROUP: "api group",
        DATABASE_OWNERS_GROUP: "database owners",
    }

    # get the active groups
    @staticmethod
    def valid(community=None):
        tmp = CommunityGroup.objects.filter(removed=False)

        if community:
            tmp = tmp.filter(community=community)

        return tmp

    def __unicode__(self):
        return unicode(self.name+ "@" + self.community.name) or u''

    def __str__(self):
        return self.name + "@" + self.community.name or u''

    @staticmethod
    def create_pre_existing_group(group, community=None):
        if group not in CommunityGroup.PRE_EXISTING_GROUPS:
            raise ValueError("The group name is not one of the pre existing ones")

        return CommunityGroup.objects.create(
            community=community,
            name=group,
            description=CommunityGroup.PRE_EXISTING_GROUPS[group],
        )

    @staticmethod
    def verify_pre_existing_group(group, comm, cu):
        if group not in CommunityGroup.PRE_EXISTING_GROUPS:
            raise ValueError("The group name is not one of the pre existing ones")

        cg = CommunityGroup.objects.get(community=comm, name=group)
        return cu in cg.members.all()

    @staticmethod
    def put_on_pre_existing_group(group, comm, cu):
        if group not in CommunityGroup.PRE_EXISTING_GROUPS:
            raise ValueError("The group name is not one of the pre existing ones")

        if not CommunityGroup.verify_pre_existing_group(group, comm, cu):
            cg = CommunityGroup.objects.get(community=comm, name=group)
            cg.members.add(cu)
            cg.save()


class QuestionSetAccessGroups(models.Model):
    from questionnaire.models import QuestionSet
    id = models.AutoField(primary_key=True)
    qset = models.ForeignKey(QuestionSet)
    communitygroup = models.ForeignKey(CommunityGroup)
    can_read = models.BooleanField(default=True)
    can_write = models.BooleanField(default=True)

    # accessMode can be either "R" or "W" (Read or Write)
    # if community is None, behavior is to deny access
    @staticmethod
    def checkAccess(accessMode, community, fingerprint, user, target_qset):
        # only do logic if useQuestionSetRBAC is enabled, else, always allow access to any questionnaire section
        if not config.useQuestionSetRBAC:
            return True
        
        if user.is_superuser or (community is not None and community.is_owner(user)) or (fingerprint is not None and user in fingerprint.unique_users()):
            return True

        # Always allow access to the intro and the outro text of a questionnaire
        if target_qset.sortid == 0 or target_qset.sortid == 99:
            return True
        
        # Allow access to an anonymous user if the fingerprint is shared
        if user.is_anonymous() and PublicFingerprintShare.objects.filter(fingerprint_id=fingerprint.id).first():
            return True

        if community is not None and community.membership == Community.MEMBERSHIP_OPEN:
            filter_arg = {}
            if accessMode == "R":
                filter_arg["can_read"] = True
            elif accessMode == "W":
                filter_arg["can_write"] = True
            else:
                raise ValueError('Invalid access mode used. Specify only either R or W for read or write mode on questionnaire section.')

            qsetGroups_CanAccess = QuestionSetAccessGroups.objects.filter(
                communitygroup__community=community,
                qset=target_qset.id,
                communitygroup=community.groups.get(name=CommunityGroup.DEFAULT_GROUP),
                **filter_arg
            )

            if qsetGroups_CanAccess.count() > 0:
                return True

        try:
            cu = CommunityUser.objects.get(community=community, user=user)
            # Check if the user has a permission, derivated from any group he belongs to inside the community
            if accessMode == "R":
                qsetGroups_CanAccess = QuestionSetAccessGroups.objects.filter(
                    communitygroup__community=community, 
                    qset=target_qset.id, 
                    can_read=True, 
                    communitygroup__members=cu
                )
            elif accessMode == "W":
                qsetGroups_CanAccess = QuestionSetAccessGroups.objects.filter(
                    communitygroup__community=community, 
                    qset=target_qset.id, 
                    can_write=True, 
                    communitygroup__members=cu
                )
            else:
                raise ValueError('Invalid access mode used. Specify only either R or W for read or write mode on questionnaire section.')

            if qsetGroups_CanAccess.count() > 0:
                return True

        except CommunityUser.DoesNotExist:
            pass

        return False

    # accessMode can be either "R" or "W" (Read or Write)
    @staticmethod
    def getFirstAccessibleQuestionSet(accessMode, community, fingerprint, user):
        accessibleQuestionSets = QuestionSetAccessGroups.getListOfAccessibleQuestionSets(accessMode, community, fingerprint, user)        
        # try to return the first element in case it exists, else return 'None'
        return accessibleQuestionSets[0] if accessibleQuestionSets else None
    
    # accessMode can be either "R" or "W" (Read or Write)
    @staticmethod
    def getListOfAccessibleQuestionSets(accessMode, community, fingerprint, user, includeIntroAndOutro = False):
        accessibleQuestionSetsList = []
        try:
            fingerprintQuestionSets = fingerprint.questionnaire.questionsets()
            for target_qset in fingerprintQuestionSets:
                # do not add the first or last qset since they are always allowed
                # (they are the intro and outro text of a questionnaire)
                if not includeIntroAndOutro:
                    if target_qset.sortid == 0 or target_qset.sortid == 99:
                        continue
                if QuestionSetAccessGroups.checkAccess(accessMode, community, fingerprint, user, target_qset):
                    accessibleQuestionSetsList = accessibleQuestionSetsList + [target_qset]
        except CommunityUser.DoesNotExist:
            return []
        return accessibleQuestionSetsList

    @staticmethod
    def getNextAccessibleQuestionSet(accessMode, community, fingerprint, user, qset_pivot):
        # this while loop will always break when any condition inside is met
        while True:
            qset_pivot = qset_pivot.next()
            if qset_pivot == None:
                return None
            canAccess = QuestionSetAccessGroups.checkAccess(accessMode, community, fingerprint, user, qset_pivot)
            if(canAccess):
                return qset_pivot

        # end case, code is never met but is still here for clarity
        return None
    
    @staticmethod
    def getPreviousAccessibleQuestionSet(accessMode, community, fingerprint, user, qset_pivot):
        # this while loop will always break when any condition inside is met
        while True:
            qset_pivot = qset_pivot.prev()
            if qset_pivot == None:
                return None
            canAccess = QuestionSetAccessGroups.checkAccess(accessMode, community, fingerprint, user, qset_pivot)
            if(canAccess):
                return qset_pivot

        # end case, code is never met but is still here for clarity
        return None


class PluginPermission(models.Model):
    communitygroup = models.ForeignKey(CommunityGroup)
    plugin = models.ForeignKey(Plugin)
    allow = models.BooleanField(default=False)

    @staticmethod
    def check_permission(community, user, plugin, fingerprint=None):
        try:
            cu = CommunityUser.objects.get(community=community, user=user)
            # allow community manager
            comm = Community.objects.filter(slug=community.slug)

            if plugin.plugin.type == Plugin.DATABASE:
                cp = PluginPermission.objects.filter(
                    communitygroup__community=community,
                    plugin=plugin.plugin,
                    allow=True,
                )

                if cp.count() == 1:  # if there is only one group that allows to access this plugin
                    if cp[0].communitygroup.name == CommunityGroup.DATABASE_OWNERS_GROUP:  # if it is the database owners plugin
                        if fingerprint is None:  # if no fingerprint is provided dont allow access
                            return False
                        # check if it is the owner or the ownership was shared with him
                        return user == fingerprint.owner or user in fingerprint.shared.all()
                    elif cp.filter(communitygroup__members=cu).count() > 0:  # if the user is in the group -> allow access
                        return True
                elif cp.count() > 0:  # if there are several groups that allow access this plugin
                    if cp.filter(communitygroup__members=cu).count() == 0:  # if the users is not in any
                        if cp.filter(communitygroup__name=CommunityGroup.DATABASE_OWNERS_GROUP).exists():  # if the database owners group is one of the groups check if its ownership
                            if fingerprint is None:
                                return False
                            return user == fingerprint.owner or user in fingerprint.shared.all()
                        elif comm.filter(owners=user).exists():  # if its a community manager allow access.
                                                                 # Note that the code gets here if the database owners
                                                                 #  group is not one of the groups that can allow access to this plugin
                            return True

                    # if it gets here the user is in at least one group that allow access and can't be the database
                    #  owners group, since no users are associated to that group
                    return True
            else:
                if comm.filter(owners=user).exists():
                    return True

                # Check if the user has a permission, derivated from any group he belongs to inside the community
                cp = PluginPermission.objects.filter(
                    communitygroup__community=community,
                    plugin=plugin.plugin,
                    allow=True,
                    communitygroup__members=cu
                )

                if cp.count() > 0:
                    return True

        except CommunityUser.DoesNotExist:
            pass

        # If there are no groups with default to allow everyone
        cgs = CommunityGroup.objects.filter(community=community, removed=False)
        if cgs.count() == 0:
            return True

        return False

# ********************************************************************
# *** to be deleted/ignored ?
# ********************************************************************
class CommunityDatabasePermission(models.Model):
    communitygroup = models.ForeignKey(CommunityGroup)
    plugin = models.ForeignKey(Plugin)
    database = models.ForeignKey(Fingerprint)

    allow = models.BooleanField(default=True)

    @staticmethod
    def check_permission(community, database, user, plugin):
        try:
            cu = CommunityUser.objects.get(community=community, user=user)
            # Check if the user has a permission, derivated from any group he belongs to inside the community
            cp = CommunityDatabasePermission.objects.filter(
                database=database, 
                communitygroup__community=community,
                plugin=plugin.plugin, 
                allow=True, 
                communitygroup__members=cu
            )

            if cp.count() > 0:
                return True

        except CommunityUser.DoesNotExist:
            pass

        #else
        return PluginPermission.check_permission(community, user, plugin, database)
# ***
# ********************************************************************
# ********************************************************************


class CommunityJoinForm(models.Model):
    community = models.ForeignKey(Community)
    question_text = models.TextField(blank=False)
    required = models.BooleanField(default=True)


class CommunityJoinFormReply(models.Model):
    commuser = models.ForeignKey(CommunityUser)
    join_form = models.ForeignKey(CommunityJoinForm)
    reply_text = models.TextField(blank=False)


class ExternalCommunity(models.Model):
    slug            = models.CharField(max_length=50, unique=True)
    sortid          = models.IntegerField(default=0)

    name            = models.CharField(max_length=100)
    description     = models.CharField(max_length=5000, null=True, blank=True)
    thumbnail       = ResizedImageField(size=[500, 200], upload_to=iconThumbnail, null=True, blank=True)
    outbound_url    = models.URLField()

