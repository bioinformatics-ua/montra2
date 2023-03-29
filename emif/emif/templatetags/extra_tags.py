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
import hashlib
import logging
import math
import re
from math import log10, pow

from constance import config
from django import template
from django import template as templates
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.template import base as template
from django.template.base import TOKEN_BLOCK, TOKEN_VAR
from django.template.defaultfilters import stringfilter
from django.template.loader import render_to_string
from djangosaml2.conf import config_settings_loader
from djangosaml2.utils import available_idps
from newsletter.models import Newsletter, Subscription

from accounts.models import Profile
from community.models import CommunitiesFavorited, CommunityExcludedExtraFields, CommunityFields, CommunityPlugins
from community.models import CommunityGroup, CommunityUser
from cookies.models import CookieConsent
from fingerprint.models import AnswerRequest
from questionnaire.models import Questionnaire
from searchengine.search_indexes import CoreEngine

register = templates.Library()
logger = logging.getLogger(__name__)


@register.assignment_tag
def is_study_manager_cuser(comm, user):
    try:
        cg = CommunityGroup.valid(community=comm).get(name="study managers")
        #print "%s in %s . Part of the \"default\" group:%s" % ( user.email , comm.name , cg.members.filter(user=user).exists() )
    except:
        logger.warn("*** \"default\" user group not found. Creating default group...")
        cg = CommunityGroup.createStudyManagers(community=comm)
        #cg = CommunityGroup(community = comm, name="default")
        #cg.save()
        
        # *** OPTIONAL : add all users to default group
        #print "*** adding all users to the \"default\" user group..."
        #cusers = comm.communityuser_set.all()
        #for cuser in cusers:
        #    cg.members.add(cuser)
        #    cg.save()  

    return cg.members.filter(user=user).exists()

@register.assignment_tag
def is_default_cuser(comm, user):
    try:
        cg = CommunityGroup.valid(community=comm).get(name="default")
        #print "%s in %s . Part of the \"default\" group:%s" % ( user.email , comm.name , cg.members.filter(user=user).exists() )
    except:
        logger.warn("*** \"default\" user group not found. Creating default group...")
        cg = CommunityGroup.createDefault(community=comm)
        #cg = CommunityGroup(community = comm, name="default")
        #cg.save()
        
        # *** OPTIONAL : add all users to default group
        #print "*** adding all users to the \"default\" user group..."
        #cusers = comm.communityuser_set.all()
        #for cuser in cusers:
        #    cg.members.add(cuser)
        #    cg.save()  

    return cg.members.filter(user=user).exists()

@register.assignment_tag
@register.filter(name="is_community_editor")
def is_editors_cuser(comm, user):
    try:
        User.objects.get(id=user.id)
    except: 
        return False
    try:
        cg = CommunityGroup.valid(community=comm).get(name=CommunityGroup.EDITORS_GROUP)
    except:
        logger.warn("*** \"default\" user group not found. Creating editors group...")
        cg = CommunityGroup.create_pre_existing_group(CommunityGroup.EDITORS_GROUP, comm)
        #cg = CommunityGroup(community = comm, name="default")
        #cg.save()
        
        # *** OPTIONAL : add all users to default group
        #print "*** adding all users to the \"default\" user group..."
        #cusers = comm.communityuser_set.all()
        #for cuser in cusers:
        #    cg.members.add(cuser)
        #    cg.save()  
    return cg.members.filter(user=user).exists()


@register.simple_tag
def get_item(obj, key):
    """
    Can be used for several purposes:
    - access at index
    - access dict key
    - invoke __getitem__ method
    """
    return obj[key]

@register.filter(name='removeh1')
@stringfilter
def removeh1(value):
    return value.replace('h1. ','')

@register.filter(name='clean')
@stringfilter
def clean(value):
    return re.sub(r'\W+', '', value)

@register.filter(name='escapedots')
@stringfilter
def escapedots(value):
    return value.replace('.','\\\\.')


@register.filter(name='replaceplicas')

@stringfilter
def replaceplicas(value):
    return value.replace('"',"'")

@register.filter(name='scaleunit')
def scaleunit(value):

    sizes = ['bytes', 'Kb', 'Mb', 'Gb', 'Tb']

    if (value == 0):
        return '0 byte'

    i = int(math.floor(math.log(value) / math.log(1024)))

    return "%d %s" % (round(value/ math.pow(1024, i), 2), sizes[i])


@register.filter(name='removehs')
@stringfilter
def removehs(value):
    value = value.replace('h0. ','')
    value = value.replace('h1. ','')
    value = value.replace('h2. ','')
    value = value.replace('h3. ','')
    value = value.replace('h4. ','')
    value = value.replace('h5. ','')
    value = value.replace('h6. ','')
    value = value.replace('h7. ','')

    return value


@register.filter(name='fixhighlight')
@stringfilter
def fixHighlight(value):
    tmp = value

    if not tmp.startswith('['):
        tmp = '['+tmp+']'

    return tmp.replace('class=highlight', 'class=\\"highlight\\"')

@register.simple_tag()
def ans_requested(question, requests, *args, **kwargs):
    try:
        question_requests = requests.filter(question = question)

        if len(question_requests) > 0:
            return render_to_string('answer_requests.html', { "requests": question_requests })

    except AnswerRequest.DoesNotExist:
        pass

    return ""

@register.filter(name='datehhmm')
@stringfilter
def datehhmm(value):
    if len(value) < 10:
        return value      
    value = value[0:10]
    return value

@register.filter(name='trim')
@stringfilter
def trim(value):
    value = value.strip()

    return value

@register.filter(name='removequotes')
@stringfilter
def removequotes(value):
    value = value.replace('"', '&quot;')

    return value

@register.filter(name='esc')
@stringfilter
def esc(value):
    return re.escape(value)

@register.filter(name='removedots')
@stringfilter
def removedots(value):
    value = value.replace('.','')

    return value

@register.filter(name='isnumber')
@stringfilter
def isnumber(value):
    return value.isdigit()


@register.filter(name='geths')
@stringfilter
def geths(value):
    value = value[0:2]
    return value


@register.filter(name='removespaces')
@stringfilter
def removespaces(value):
    value = value.replace('h1. ','')
    value = value.replace(',','')
    value = value.replace('/','')
    result = value.replace(' ','')

    return result

@register.filter(name='hash')
@stringfilter
def hash(value):
    return hashlib.sha224(value).hexdigest()

@register.filter(name='truncate')
@stringfilter
def truncate(value):
    result = value[:30]

    return result

@register.filter(name='truncatewithdots')
@stringfilter
def truncatewithdots(value):
    result = value[:30]
    if len(value) > 30:
        result = result + "..."

    return result

@register.filter(name='splitfirst')
@stringfilter
def splitfirst(value):
    if value:
        return value.split(' ', 1)[0]

    return ''

@register.filter(name='ignorefirst')
@stringfilter
def ignorefirst(value):
    try:
        if value:
            return value.split(' ', 1)[1]
    except:
        pass

    return ''

@register.filter(name='captioned')
@stringfilter
def captioned(value):
    exclusion_list = ['publication', 'choice-tabular', 'choice', 'choice-freeform','choice-multiple','choice-multiple-freeform','choice-multiple-freeform-options']

    return value not in exclusion_list

@register.filter(name='is_usecase')
@stringfilter
def is_usecase(value):

    return bool(re.match('use', value, re.I))

@register.filter
def whitespacesplit(str):
    words = []

    for m in re.finditer(r'"(.*?)"', str):
        words.append(m.group(1))
        str = str.replace(m.group(0), "")

    words = words + str.strip().split()

    return words

@register.filter(name='commasplit')
@stringfilter
def commasplit(str):
    words = []

    words = words + str.strip().split(',')

    return words

@register.filter
def ellipsis(str, size):
    if str:
        if(len(str) > size):
            return str[:size]+"..."

        return str

    return None

@register.filter
def isDataCustodian(profiles):
    try:
        dc = Profile.objects.get(name="Data Custodian")

        if dc in profiles:
            return True
    except Profile.DoesNotExist:
        pass

    return False

@register.filter
def isResearcher(profiles):
    try:
        rs = Profile.objects.get(name="Researcher")

        if rs in profiles:
            return True
    except Profile.DoesNotExist:
        pass

    return False

def fingerprints_list(comm):

    try:
        objs = None
        if comm:
            objs = comm.questionnaires.filter(disable=False)
        else:
            objs = Questionnaire.objects.filter(disable=False)
    except:
        pass
    results = {}
    for q in objs:
        results[q.id] = q.name


    return results

@register.assignment_tag
def find_comm(user_comms, fingerprint_comms):
    for f_comm in fingerprint_comms:
        for user_comm in user_comms:
            if user_comm.slug == f_comm:
                return user_comm

    return None

@register.simple_tag
def find_field_value(database, field):

    if isinstance(field, CommunityFields):
        inner_field = field.field
    else:
        inner_field = field

    if database is None:
        return ''

    if inner_field.type == 'datepicker':
        return datehhmm(database.fields.get("%s_dt" % inner_field.slug, ''))
    elif inner_field.type == 'numeric':
        if isinstance(field, CommunityFields) and field.apply_formatting:
            return human_format(database.fields.get("%s_d" % inner_field.slug, ''))
        else:
            value = database.fields.get("%s_d" % inner_field.slug, '')
            return "%.0d" % value \
                if type(value) == float \
                else ''
    else:
        return database.fields.get("%s_t" % inner_field.slug, '')

@register.filter
def human_format(num):
    if num:
        num = float('{:.3g}'.format(num))
        l10 = int(log10(num))
        magnitude = 0
        if(l10 > 0):
            magnitude = int(( l10 // 3 ))
            if(magnitude > 0):
                num = num / (pow(10,3*magnitude))
        return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])
    else:
        return ''

@register.filter(name='split')
def split(value, key):
    return list(filter(lambda x : x!= "", value.split(key)))

@register.assignment_tag
def find_sort_param(params, slug):
    try:
        return params[slug]
    except:
        return {}

@register.assignment_tag
def find_all_plugin_groups(plugin_list):
    all_plugins_group = [plugin.plugin_group for plugin in plugin_list]
    return set(all_plugins_group)

def fingerprints_list_user(user, use_slugs=False):

    interests = Questionnaire.objects.filter(disable=False)
    quests = []

    try:
        for inter in interests:
            if inter.disable==False:
                quests.append(inter)
    except:
        pass

    results = {}
    for q in quests:
        if use_slugs:
            results[q.slug] = q.name
        else:
            results[q.id] = q.name

    return results

def profiles_list_user(user):
    profiles = user.emif_profile.profiles.all()
    results = {}
    for p in profiles:
        results[p.id] = p.name

    return results

def show_profiles(user):

    return {'profiles':profiles_list_user(user)}
register.inclusion_tag('reusable_blocks/menu_ttags_profiles.html')(show_profiles)

def show_fingerprints_interests_profile(user):

    return {'fingerprints':fingerprints_list_user(user)}
register.inclusion_tag('reusable_blocks/menu_ttags_interests.html')(show_fingerprints_interests_profile)

def show_fingerprints_interests(user):

    return {'fingerprints':fingerprints_list_user(user)}
register.inclusion_tag('reusable_blocks/menu_ttags.html')(show_fingerprints_interests)

@register.simple_tag
def show_subscription(user):
    link = None
    label = None
    try:
        newsl = Newsletter.objects.get(slug='emif-catalogue-newsletter')

        link="newsletter/"+newsl.slug+"/subscribe"
        label="Subscribe Newsletter"

        # create subscription
        user_sub = None
        try:
            subscription = Subscription.objects.get(user=user,  newsletter=newsl)

            if not subscription.unsubscribed:
                link = "newsletter/"+newsl.slug+"/unsubscribe"
                label = "Unsubscribe Newsletter"
        except:
            pass


    except Newsletter.DoesNotExist:
        print "Problem finding default newsletter"

    return '<a href="'+str(link)+'" class="navbar-link"><i class="fas fa-fw fa-rss"></i>&nbsp;'+str(label)+'</a>'

def show_fingerprints(activesubmenu, comm):

    fingerprints = None

    return {
        'fingerprints': fingerprints_list(comm),
        'activesubmenu': activesubmenu,
        'comm': comm
    }
register.inclusion_tag('reusable_blocks/menu_ttags.html')(show_fingerprints)

def show_questionnaires(activesubmenu, comm):

    questionnaires = None

    return {
        'questionnaires': fingerprints_list(comm),
        'activesubmenu': activesubmenu,
        'comm': comm
    }
register.inclusion_tag('reusable_blocks/menu_questionnaires.html')(show_questionnaires)


def show_fingerprints_for_search(user):

    return {'fingerprints':fingerprints_list_user(user)}
register.inclusion_tag('reusable_blocks/menu_ttags_for_search.html')(show_fingerprints_for_search)

def show_fingerprints_dropdown(user, sort_params):

    return {'fingerprints':fingerprints_list_user(user, use_slugs=True), 'sort_params': sort_params}
register.inclusion_tag('reusable_blocks/selectfdropdown.html')(show_fingerprints_dropdown)


def show_fingerprints_for_statistics():

    return {'fingerprints':fingerprints_list()}
register.inclusion_tag('reusable_blocks/menu_ttags_for_statistics.html')(show_fingerprints_for_statistics)



class GlobalVariable( object ):

    def __init__( self, varname, varval ):
        self.varname = varname
        self.varval  = varval

    def name( self ):
        return self.varname

    def value( self ):
        return self.varval

    def set( self, newval ):
        self.varval = newval


class GlobalVariableSetNode( template.Node ):

    def __init__( self, varname, varval ):
        self.varname = varname
        self.varval  = varval

    def render( self, context ):
        gv = context.get( self.varname, None )
        if gv:
            gv.set( self.varval )
        else:
            gv = context[self.varname] = GlobalVariable( self.varname, self.varval )
        return ''


def setglobal( parser, token ):
    try:
        tag_name, varname, varval = token.contents.split(None, 2)
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires 2 arguments" % token.contents.split()[0])
    return GlobalVariableSetNode( varname, varval )

register.tag( 'setglobal', setglobal )


class GlobalVariableGetNode( template.Node ):

    def __init__( self, varname ):
        self.varname = varname

    def render( self, context ):
        try:
            return context[self.varname].value()
        except AttributeError:
            return ''

@register.simple_tag()
def multiply(a, b, *args, **kwargs):
    # you would need to do any localization of the result here
    return a * b

def getglobal( parser, token ):
    try:
        tag_name, varname = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires arguments" % token.contents.split()[0])
    return GlobalVariableGetNode( varname )


register.tag( 'getglobal', getglobal )

class GlobalVariableIncrementNode( template.Node ):
  def __init__( self, varname ):
    self.varname = varname
  def render( self, context ):
    gv = context.get( self.varname, None )
    if gv is None:
      return ''
    gv.set( int(gv.value()) + 1 )
    return ''
def incrementglobal( parser, token ):
  try:
    tag_name, varname = token.contents.split(None, 1)
  except ValueError:
    raise template.TemplateSyntaxError("%r tag requires arguments" % token.contents.split()[0])
  return GlobalVariableIncrementNode(varname)

register.tag( 'incrementglobal', incrementglobal )

class VersionNode( template.Node ):
  def __init__( self, varname ):
    self.varname = varname
  def render( self, context ):
    return get_version()

def get_version():
    return settings.VERSION + " " + settings.VERSION_DATE

def get_version_tag(parser, token):
    return VersionNode('')
register.tag( 'get_version', get_version_tag )


@register.simple_tag
def slogan():
    return "Discover the right data for your research"


@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False

@register.simple_tag
def idps_dropdown():
    return render_to_string('reusable_blocks/idp_dropdowns.html',
        {
            "idps": available_idps(config_settings_loader()).items(),
            "base": settings.BASE_URL
        })

#lmf
@register.simple_tag
def user_in_community(community, user):
    if community.belongs(user) or community.membership!='invitation':
        return ""
    return "hidden"
#***

def belong_community(community, user):

    #tmp = '<a href="c/'+community.slug+'" class="btn btn-grey btn-panel-body"><i class="fas fa-fw fa-clock"></i> &nbsp;PENDING</a>'
    tmp = ''

    if ( community.is_owner(user) or (community.membership == 'open')):
        tmp = '<a href="community/'+community.slug+'/questionnaires" class="btn btn-blue btn-panel-body"><i class="fas fa-fw fa-folder-open"></i></i>&nbsp; OPEN</a>'        
    elif ( community.belongs(user) != None ):
        tmp = '<a href="community/'+community.slug+'/questionnaires" class="btn btn-blue btn-panel-body"><i class="fas fa-fw fa-folder-open"></i>&nbsp; OPEN</a>'
    elif ( community.membership == 'public' ):
        tmp = '<a href="community/'+community.slug+'/questionnaires" class="btn btn-blue btn-panel-body"><i class="fas fa-plus"></i></i>&nbsp; JOIN</a>'
    elif ( community.membership == 'invitation' ):
        tmp = '<span class="btn btn-grey btn-panel-body">By Invitation Only</span>'
    #elif (community.membership == 'members' ):
    #    tmp = '<button class="btn btn-blue btn-panel-body" onclick="communityMemberConfirmation()"><i class="fas fa-fw fa-plus"></i>&nbsp; JOIN</button><script>function communityMemberConfirmation() { if (confirm("Requests to join this community are limited to project partners.\\nBy continuing, you confirm that you are a partner of the project.")== true) {window.open("c/'+community.slug+'","_self")}; }</script>'
    else:
        tmp = '<a href="community/'+community.slug+'/questionnaires" class="btn btn-blue btn-panel-body"><i class="fas fa-plus"></i>&nbsp; JOIN</a>'


    return {
    'text': tmp
    }
register.inclusion_tag('reusable_blocks/join_button.html')(belong_community)

@register.filter(name='community_owner')
def community_owner(comm, user):
    try:
        comm.owners.get(id=user.id)
    except User.DoesNotExist:
        return False
    return True

@register.filter(name='community_favorited')
def community_favorited(comm, user):
    query = CommunitiesFavorited.objects.filter(community=comm, user=user)
    return query.count() > 0


@register.filter(name='cookies_consented')
def cookies_consented(user):
    try:
        cookie_consent = CookieConsent.objects.get(user=user)
    except CookieConsent.DoesNotExist:
        return False
    return cookie_consent.consented if cookie_consent else False


@register.filter(name='user_belongs')
def user_belongs(comm, user):
    return comm.belongs(user) != None
    
@register.filter(name='listsort')
def listsort(value):
    return sorted(value)


@register.filter(name='plugin_sortid')
def plugin_sortid(value, comm):
    tmp = None
    try:
        cp = comm.communityplugins_set.get(plugin=value.plugin)

        tmp = cp.sortid

    except CommunityPlugins.DoesNotExist:
        pass

    return tmp

@register.filter(name='comm_user_dbs')
def comm_user_dbs(comm, user):

    c = CoreEngine()
    results = c.search_fingerprint('user_t:%s' % user.username, qop='OR')
    return len(results)


"""
jQuery templates use constructs like:
    {{if condition}} print something{{/if}}
This, of course, completely screws up Django templates,
because Django thinks {{ and }} mean something.
Wrap {% verbatim %} and {% endverbatim %} around those
blocks of jQuery templates and this will try its best
to output the contents with no changes.
"""



class VerbatimNode(template.Node):

    def __init__(self, text):
        self.text = text
    
    def render(self, context):
        return self.text


@register.tag
def verbatim(parser, token):
    text = []
    while 1:
        token = parser.tokens.pop(0)
        if token.contents == 'endverbatim':
            break
        if token.token_type == TOKEN_VAR:
            text.append('{{')
        elif token.token_type == TOKEN_BLOCK:
            text.append('{%')
        text.append(token.contents)
        if token.token_type == TOKEN_VAR:
            text.append('}}')
        elif token.token_type == TOKEN_BLOCK:
            text.append('%}')
    return VerbatimNode(''.join(text))

@register.filter(name='format')
def format(value, fmt):
    return fmt.format(value)

@register.simple_tag
def get_communityfields(comm, questionnaire, view=None):
    view = viewExternalToInternal(view)

    return comm.get_communityfields(questionnaire, view)

@register.simple_tag
def get_uniquecommunityfields(comm, questionnaire, view=None):
    view = viewExternalToInternal(view)
    fields = comm.get_communityfields(questionnaire, view)

    #return list with unique slugs
    unique_fields = []
    already_added = []
    for f in fields:
        if f.field.slug not in already_added:
            unique_fields.append(f)
            already_added.append(f.field.slug)

    return unique_fields


@register.simple_tag
def get_excluded_extra_community_fields(comm, questionnaire, view=None):
    view = viewExternalToInternal(view)

    return CommunityExcludedExtraFields.objects.filter(
        community=comm, questionnaire=questionnaire, view=view
    ).values_list("name", flat=True)


def viewExternalToInternal(view):
    if view == 'table':
        view = 'TB'
    elif view == 'card':
        view = 'CD'
    elif view == 'list':
        view = 'LT'
    
    return view

@register.filter(name='config_vars')
def config_vars(content):
    content = content.replace('{{config.client_wrapper_name}}', config.client_wrapper_name)
    return content

@register.filter(name='user_in_community_group')
def user_in_community_group(community, user):

    try:
        cu = CommunityUser.objects.get(community=community, user=user)
    except CommunityUser.DoesNotExist:
        return False

    return CommunityGroup.verify_pre_existing_group(CommunityGroup.API_GROUP, community, cu)