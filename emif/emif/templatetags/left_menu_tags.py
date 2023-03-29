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
from django import template as templates
from django.conf import settings

from community.models import Community, CommunityGroup, CommunityUser, PluginPermission
from developer.models import Plugin

register = templates.Library()


def get_from_context(key, context):
    """
    Auxiliary function to retrieve a given key from the current context.
    Since the context is a list of dictionaries, it is necessary to iterate over the list and inspect each dictionary
    separately. This function will return the key's corresponding value, if it exists or False otherwise.
    Args:
        key: key to lookup in the current context
        context: current django template's context

    Returns: either the value, if found, or False otherwise
    """

    for c in context:
        try:
            value = c[key]
        except KeyError:
            continue
        else:
            return value
    return False


@register.inclusion_tag('left_navigation_bar/menu_object.html', takes_context=True)
def menu_entry(context, menu_entry):
    """
    Custom inclusion tag defined for a menu object. The menu object is defined as a generic template that will extend
    the template passed in the menu_entry. This allows the menu to be composed of different templates that can be used
    for different purposes. This method's input comes from the usage of the custom tag itself.

    Args:
        menu_entry: Current menu entry to be rendered.

    Returns:
        A dictionary containing the template to be rendered and the menu entry's information.

    """
    template = menu_entry['template']
    activemenu = get_from_context('activemenu', context)
    activesubmenu = get_from_context('activesubmenu', context)
    return {'template': template,
            'menu_entry': menu_entry,
            'activemenu': activemenu,
            'activesubmenu': activesubmenu}


@register.inclusion_tag('left_navigation_bar/left_navigation_bar.html', takes_context=True)
def left_navigation_bar(context):
    """
    Custom inclusion tag defined for the left navigation bar of the platform.
    This method will decide which menu entries are going to be displayed based on the current context. The context is
    passed internally by Django because the decorator takes the argument takes_context as True. Some entries are
    displayed based on information that exists in the request as well, like the user authentication status.
    It will return a dictionary containing a "displayed_menus" list. Each entry of this list contains a dictionary
    (somehow like a JSON) that has all the information about each menu entry.
    The output from this method is to be consumed by the Django Template responsible for rendering the left navigation
    bar.
    Args:
        context: Current template's context.

    Returns:
        A list of dictionaries containing each menu entry.

    See Also:
        https://docs.djangoproject.com/en/dev/howto/custom-template-tags/#howto-custom-template-tags-inclusion-tags

    Raises:
        KeyError if the request does not exist in the current context.

    Notes:
        Instead of iterating over the context looking for the required information, it can be passed directly from
        the template. This way, it's possible to save some iteration cycles and speed-up the process.

    """
    listed_menus_entries = []
    request = get_from_context('request', context)
    activemenu = get_from_context('activemenu', context)
    activesubmenu = get_from_context('activesubmenu', context)
    comm = ""

    if request.user.is_authenticated:
        listed_menus_entries.extend([homeMenu()])
        comm = get_from_context('comm', context)
        if not comm and settings.SINGLE_COMMUNITY:
            if Community.objects.count() > 1:
                comm = Community.objects.all()[0]
                # This is hacky as hell and we dont have guarantees that it will return the
                #  expected community, however, on MSDA it is being done this way to automatically
                #  redirect to the MSDA community.
                # I implemented this edge case this way just to keep consistency.
            else:
                comm = Community.objects.get()
        if comm:
            listed_menus_entries.extend(catalogue(comm, request))
            listed_menus_entries.extend(otherComponents(comm))
            listed_menus_entries.extend(plugins(comm, request))
            if request.user.is_staff or comm.is_owner(request.user):
                listed_menus_entries.extend(manage(comm))

            listed_menus_entries.extend(api(comm, request))
        listed_menus_entries.extend(portal(request))

        # Admin Section is the same in single and multiple communities
        if request.user.is_staff:
            listed_menus_entries.extend([adminSection(), adminMenu()])
        
        if request.user.emif_profile.has_group('importers') or request.user.is_superuser:
            listed_menus_entries.extend([importMenu()])

        if request.user.emif_profile.has_group('exporters') or request.user.is_superuser:
            listed_menus_entries.extend([exportMenu()])

    # If the user is not authenticated, display the basic menus that do not require authentication.
    if not request.user.is_authenticated:
        listed_menus_entries = [signInMenu(), portalSection(), aboutMenu(), historyMenu()]
        if config.faqMenu:
            listed_menus_entries.append(faqMenu())
        listed_menus_entries.append(docMenu())

    return {
        "displayed_menus": listed_menus_entries,
        "activemenu": activemenu,
        "activesubmenu": activesubmenu, 
        "user": request.user,
        "comm": comm
    }


################################################
# Menu's Logic
################################################
def catalogue(comm, request):
    """
    This function will decide which sub-menus under the Catalogue entry should be displayed
     to the user depending on the community's conditions in terms of:
    - The amount of questionnaires that it has.
    - Whether the Private Link option is enabled in the settings.
    If the community does not have any questionnaire, it will return an empty list,
    meaning that the Catalogue option will not be displayed,

    Args:
        comm: the current context's community
        request: the current request.

    Returns:
        A list containing the menus and sub-menus to be displayed to the user. Might be an empty list if the community
        does not has any questionnaire associated.

    """
    subMenus = []
    all_questionnaires = comm.questionnaires.all()
    questionnaires_length = len(all_questionnaires)

    if questionnaires_length > 1:
        subMenus.extend([allQuestionnairesMenu(comm)])
        for questionnaire in all_questionnaires:
            subMenus.extend([subMenuSection(questionnaire.name)])
            subMenus.extend(_catalogueByQuestionnaire(comm, questionnaire, request.user))
    elif questionnaires_length == 1:
        questionnaire = all_questionnaires[0]
        subMenus.extend(_catalogueByQuestionnaire(comm, questionnaire, request.user))
    else:
        return []
    if config.privateLinksMenu:
        subMenus.extend([subMenuSection(""), privateLinksMenu(comm)])
    return [catalogueMenu("Catalogue" if config.portal_installation else "Databases", subMenus)]


def _catalogueByQuestionnaire(comm, questionnaire, user):
    """
    This function will generate the sub-menus for the given questionnaire under the Catalogue entry. It will also decide
     if the Search and Custom View sub-menus are going to be displayed if they are enabled in the settings.
    Args:
        comm: the current context's community
        questionnaire:  the current context's questionnaire

    Returns:
        A list of sub-menus to be displayed to the user based on the given community and questionnaire.
    """
    subMenus = [databasesMenu(comm, questionnaire), personalMenu(comm, questionnaire)]

    cg_editors = CommunityGroup.valid(community=comm).get(name=CommunityGroup.EDITORS_GROUP)

    if cg_editors.members.filter(user=user).exists() or \
        comm.owners.filter(id=user.id).first() == user or \
            user.is_staff:
        subMenus.append(newEntryMenu(comm, questionnaire))

    if config.searchMenu:
        subMenus.append(searchMenu(comm, questionnaire))
    if config.customViewMenu:
        subMenus.append(customViewMenu(comm, questionnaire))
    return subMenus


def otherComponents(comm):
    """
    This function will determine whether the menus Map and Dashboard are going to be displayed to the user if they are
    enabled in the settings.
    Args:
        comm: the current context's community

    Returns:
        A list containing the menus to be displayed to the user based on the given community.

    """
    menus = []
    if config.mapMenu:
        menus.extend([mapMenu(comm)])
    if config.dashboardMenu:
        menus.extend([dashboardMenu(comm)])
    return menus


def plugins(comm, request):
    """
    This function will generate the menu entries containing the plugins of the given community. It will also decide
    whether each plugin should be displayed or not based on the user's permissions.

    Args:
        comm: the current context's community.
        request: the current context's request.

    Returns:
        A list containing the menu entries to be displayed containing the community plugins that are available for the
        given user.

    """
    plugins_list = comm.getAllCommunityPlugins()
    plugins_menu_entries = []
    plugins_group_index = {}
    for pluginComm in plugins_list:
        if PluginPermission.check_permission(comm, request.user, pluginComm):
            plugin_group = pluginComm.plugin.plugin_group

            if pluginComm.plugin.plugin_view == Plugin.EXT_LINK:
                menu_entry_type = pluginMenu(pluginComm.plugin, pluginComm.plugin.getLatestPath(), sublink=(plugin_group != ''), extLink=True)
            else:
                if pluginComm.plugin.type == Plugin.THIRD_PARTY:
                    type = "tp"
                else:
                    type = "gp"
                url = "c/{}/apps/{}/{}".format(comm.slug, type, pluginComm.plugin.slug)
                menu_entry_type = pluginMenu(pluginComm.plugin, url, sublink=(plugin_group != ''))

            if plugin_group == "":
                plugins_menu_entries.append((menu_entry_type, pluginComm.plugin.plugin_index))
            else:
                if plugin_group not in plugins_group_index:
                    plugins_group_index[plugin_group] = len(plugins_menu_entries)
                    plugins_menu_entries.append((pluginGroupMenu(plugin_group), pluginComm.plugin.plugin_group_index))
                
                plugins_menu_entries[plugins_group_index[plugin_group]][0]["menu_entry_submenu"]\
                    .append((menu_entry_type, pluginComm.plugin.plugin_index))    
    
    for plugin_group in plugins_group_index:
        all_subplugins = plugins_menu_entries[plugins_group_index[plugin_group]][0]["menu_entry_submenu"]
        plugins_menu_entries[plugins_group_index[plugin_group]][0]["menu_entry_submenu"] = [pl[0] for pl in sorted(all_subplugins, key=lambda t: t[1])]

    return [pl[0] for pl in sorted(plugins_menu_entries, key=lambda t: t[1])]


def manage(comm):
    """
    This function will generate the sub-menu entries associated with the Manage menu entry. It will also decide which
    entries are to be displayed based on the settings and the given community's condition. If the community does not
    have any questionnaire, it will return an empty list, meaning that the Manage option will not be displayed.
    Args:
        comm: The current context's community.

    Returns:
        A list containing the menu and sub-menu entries for the Manage option. Can be an empty list if the community
        does not have any questionnaire associated.

    """
    subMenus = [descriptionMenu(comm), usersMenu(comm), joinFormMenu(comm), groupsMenu(comm)]
    if config.componentsMenu:
        subMenus.extend([componentsMenu(comm)])
    if config.communicationMenu:
        subMenus.extend([communicationMenu(comm)])
    if not comm.auto_accept:
        subMenus.extend([draftsMenu(comm)])
    subMenus.extend([settingsMenu(comm)])

    all_questionnaires = comm.questionnaires.all()
    questionnaires_length = len(all_questionnaires)
    if questionnaires_length > 1:
        for questionnaire in all_questionnaires:
            subMenus.extend([subMenuSection(questionnaire.name)])
            subMenus.extend(_manageByQuestionnaire(comm, questionnaire, show_qsets=True))
    elif questionnaires_length == 1:
        questionnaire = all_questionnaires[0]
        subMenus.extend(_manageByQuestionnaire(comm, questionnaire, show_qsets=True))
    else:
        return []
    notifications = None
    if comm.pending:
        notifications = len(comm.pending())
    return [manageMenu(subMenus, notifications)]


def _manageByQuestionnaire(comm, questionnaire, show_qsets=True):
    """
    This function will generate the sub-menus for the given questionnaire under the Manage entry.
    It will also decide if the Question Set sub-menu is going to be displayed if it is enabled in the settings.
    Args:
        comm: the current context's community
        questionnaire:  the current context's questionnaire
        show_qsets: whether to show Question Sets sub menu entry or not

    Returns:
        A list of sub-menus to be displayed to the user under the Manage entry based on the given community and
        questionnaire.
    """
    subMenus = [
        viewsMenu(comm, questionnaire),
    ]
    if config.questionSetsMenu and show_qsets:
        subMenus.extend([questionSetsMenu(comm, questionnaire)])
    return subMenus


def api(comm, request):
    """
    This function will generate the API menu entry if it is enabled in the settings and the user has permissions to
    see it. Otherwise it will return an empty list meaning that the API menu entry will not be displayed.
    Args:
        comm: the current context's community
        request: the current request.

    Returns:
        A list containing the API menu entry to be displayed to the user if it is enabled in the settings and the user
        has permissions to see it.

    """
    cg_api = CommunityGroup.valid(community=comm).get(name=CommunityGroup.API_GROUP)
    cu = None
    try:
        cu = CommunityUser.objects.get(user=request.user, community=comm)
    except CommunityUser.DoesNotExist:
        pass

    if config.apiMenu and cu is not None \
            and (((comm.owners.filter(id=request.user.id).first() == request.user
                  or comm.belongs(request.user))
                  and CommunityGroup.verify_pre_existing_group(CommunityGroup.API_GROUP, comm, cu))
                 or request.user.is_staff):
        url = ""
        if comm:
            url = "c/{}/".format(comm.slug)
        url += "api-info"
        return [apiMenu(url)]
    return []


def portal(request):
    """
    This function will generate all the menu entries under the "Portal" section on the left-menu.
    Each entry will be displayed if it is enabled in the settings.
    The developers menu is shown if the user has permissions to do so.
    Args:
        request: the current request.

    Returns:
        A list containing the menu entries of the left-menu under the "Portal" section.

    """
    menus = [portalSection()]
    if config.aboutMenu:
        menus.extend([aboutMenu()])
    if config.historyMenu:
        menus.extend([historyMenu()])
    if config.faqMenu:
        menus.extend([faqMenu()])
    if config.docMenu:
        menus.extend([docMenu()])
    if config.contactMenu:
        menus.extend([contactMenu()]) 
    menus.extend([profileMenu()])
    if config.notificationsMenu:
        menus.extend([notificationsMenu()])
    if config.jobQueueMenu:
        menus.extend([jobQueueMenu()])
    if request.user.emif_profile.has_group('developers') or request.user.is_staff:
        menus.extend([developersMenu()])
    menus.extend([signOutMenu()])
    return menus


################################################
# Menu's Definition
################################################
# Sections labels
def portalSection():
    """
    Defines the menu entry corresponding to the "Portal" header in the left-menu.

    Returns:
        A dictionary containing the menu entry with its corresponding attributes to be rendered by the template.

    """
    return {"text": "Portal",  "template": "left_navigation_bar/menu_heading.html"}


def adminSection():
    """
    Defines the menu entry corresponding to the "Admin" header in the left-menu.

    Returns:
        A dictionary containing the menu entry with its corresponding attributes to be rendered by the template.

    """
    return {"text": "Admin",   "template": "left_navigation_bar/menu_heading.html"}


def subMenuSection(text):
    """
    Defines the sub-menu entry corresponding to the questionnaire's name header in the left-menu.

    Args:
        text: questionnaire's name.

    Returns:
        A dictionary containing the sub-menu entry with its corresponding attributes to be rendered by the template.

    """
    return {"text": text,      "template": "left_navigation_bar/submenu_heading.html"}


# Buttons
def catalogueMenu(text, subMenus):
    """
    Defines the menu entry corresponding to the "Databases" option in the left-menu.
    Args:
        text: the entry's text.
        subMenus: a list of dictionaries containing the sub-menus for this entry.

    Returns:
        A dictionary containing the menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "databases",
                "url": "",
                "text": text,
                "template": "left_navigation_bar/menu_entry.html",
                "icon": "fas fa-fw fa-database",
                "menu_entry_submenu": subMenus
            }


def manageMenu(subMenus, notifications):
    """
    Defines the menu entry corresponding to the "All" option in the left-menu.
    Args:
        subMenus: a list of dictionaries containing the sub-menus for this entry.

    Returns:
        A dictionary containing the sub-menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "mancomm",
                "url": "",
                "text": "Manage",
                "template": "left_navigation_bar/menu_entry_notifications.html" if notifications else  "left_navigation_bar/menu_entry.html",
                "icon": "fas fa-fw fa-wrench",
                "menu_entry_submenu": subMenus,
                "notifications": notifications
            }


def homeMenu():
    """
    Defines the menu entry corresponding to the "Home" option in the left-menu.

    Returns:
        A dictionary containing the menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "home",
                "url": "",
                "text": "Home",
                "template": "left_navigation_bar/menu_entry.html",
                "icon": "fas fa-fw fa-home",
            }


def aboutMenu():
    """
    Defines the menu entry corresponding to the "About" option in the left-menu.

    Returns:
        A dictionary containing the menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "about",
                "url": "about",
                "text": "About",
                "template": "left_navigation_bar/menu_entry.html",
                "icon": "fas fa-fw fa-bookmark",
            }


def historyMenu():
    """
    Defines the menu entry corresponding to the "History" option in the left-menu.

    Returns:
        A dictionary containing the menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "history",
                "url": "controlversion/history",
                "text": "History",
                "template": "left_navigation_bar/menu_entry.html",
                "icon": "fas fa-fw fa-history",
            }


def faqMenu():
    """
    Defines the menu entry corresponding to the "FAQ" option in the left-menu.

    Returns:
        A dictionary containing the menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "faq",
                "url": "faq",
                "text": "FAQ",
                "template": "left_navigation_bar/menu_entry.html",
                "icon": "fas fa-fw fa-question-circle",
            }


def docMenu():
    """
    Defines the menu entry corresponding to the "Documentation" option in the left-menu.

    Returns:
        A dictionary containing the menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "documentation",
                "url": "documentation",
                "text": "Get Started",
                "template": "left_navigation_bar/menu_entry.html",
                "icon": "fas fa-fw fa-book",
            }


def contactMenu():
    """
    Defines the menu entry corresponding to the "Contact" option in the left-menu and its sub-menu entries.

    Returns:
        A dictionary containing the menu entry with its corresponding attributes to be rendered by the template.
         It also contains the contact sub-menu entries "Bug Report" and "Feedback".

    """
    if config.bug_report:
        return {
            "id": "feedback",
            "url": "",
            "text": "Feedback",
            "template": "left_navigation_bar/menu_entry.html",
            "icon": "fas fa-fw fa-phone",
            "menu_entry_submenu": [
                {
                    "id": "bugreport",
                    "url": "bugreport",
                    "text": "Bug Report",
                    "template": "left_navigation_bar/submenu_entry.html",
                    "icon": "fas fa-fw fa-bug",
                },
                {
                    "id": "suggestions",
                    "url": "feedback",
                    "text": "Suggestions",
                    "template": "left_navigation_bar/submenu_entry.html",
                    "icon": "fas fa-fw fa-info",
                }
            ]
        }
    else:
        return {
            "id": "feedback",
            "url": "feedback",
            "text": "Feedback",
            "template": "left_navigation_bar/menu_entry.html",
            "icon": "fas fa-fw fa-phone",
        }


def allQuestionnairesMenu(comm):
    """
    Defines the sub-menu entry corresponding to the "All" option in the left-menu.
    Args:
        comm: the current context's community object

    Returns:
        A dictionary containing the sub-menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "all",
                "url": "community/{}/questionnaires".format(comm.slug),
                "text": "All",
                "template": "left_navigation_bar/submenu_entry.html",
                "icon": "",
            }


def databasesMenu(comm, questionnaire):
    """
    Defines the sub-menu entry corresponding to the "Databases" option in the left-menu.
    Args:
        comm: the current context's community object.
        questionnaire: the current context's questionnaire.

    Returns:
        A dictionary containing the sub-menu entry with its corresponding attributes to be rendered by the template.
    
    """
    return {
                "id": "questionnaire-{}".format(questionnaire.slug),
                "url": "c/{}/q/{}".format(comm.slug, questionnaire.slug),
                "text": "Databases",
                "template": "left_navigation_bar/submenu_entry.html",
                "icon": "fas fa-fw fa-database",
            }


def newEntryMenu(comm, questionnaire):
    """
    Defines the sub-menu entry corresponding to the "New Entry" option in the left-menu.
    Args:
        comm: the current context's community object.
        questionnaire: the current context's questionnaire.
        
    Returns:
        A dictionary containing the sub-menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "add",
                "url": "c/{}/add/{}/0".format(comm.slug, questionnaire.id),
                "text": "New Entry",
                "template": "left_navigation_bar/submenu_entry.html",
                "icon": "fas fa-fw fa-plus-circle",
            }


def personalMenu(comm, questionnaire):
    """
    Defines the sub-menu entry corresponding to the "Personal" option in the left-menu.
    Args:
        comm: the current context's community object.
        questionnaire: the current context's questionnaire.

    Returns:
        A dictionary containing the sub-menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "personal-{}".format(questionnaire.slug),
                "url": "c/{}/q/{}/databases".format(comm.slug, questionnaire.slug),
                "text": "Personal",
                "template": "left_navigation_bar/submenu_entry.html",
                "icon": "fas fa-fw fa-heart",
            }


def searchMenu(comm, questionnaire):
    """
    Defines the sub-menu entry corresponding to the "Advanced Search" option in the left-menu.
    Args:
        comm: the current context's community object.
        questionnaire: the current context's questionnaire.

    Returns:
        A dictionary containing the sub-menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "search-{}".format(questionnaire.slug),
                "url": "c/{}/advancedSearch/{}/1".format(comm.slug, questionnaire.id),
                "text": "Advanced Search",
                "template": "left_navigation_bar/submenu_entry.html",
                "icon": "fas fa-fw fa-search",
            }


def customViewMenu(comm, questionnaire):
    """
    Defines the sub-menu entry corresponding to the "Custom View" option in the left-menu.
    Args:
        comm: the current context's community object.
        questionnaire: the current context's questionnaire object

    Returns:
        A dictionary containing the sub-menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "datatable-{}".format(questionnaire.slug),
                "url": "c/{}/q/{}/custom-view".format(comm.slug, questionnaire.slug),
                "text": "Custom View",
                "template": "left_navigation_bar/submenu_entry.html",
                "icon": "fas fa-fw fa-th",
            }


def privateLinksMenu(comm):
    """
    Defines the sub-menu entry corresponding to the "Private Links" option in the left-menu.
    Args:
        comm: the current context's community object.

    Returns:
        A dictionary containing the sub-menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "private",
                "url": "c/{}/public/fingerprint".format(comm.slug),
                "text": "Private Links",
                "template": "left_navigation_bar/submenu_entry.html",
                "icon": "fas fa-fw fa-share",
            }


def mapMenu(comm):
    """
    Defines the menu entry corresponding to the "Map" option in the left-menu.
    Args:
        comm: the current context's community object.

    Returns:
        A dictionary containing the sub-menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "geo",
                "url": "c/{}/geo".format(comm.slug),
                "text": "Map",
                "template": "left_navigation_bar/menu_entry.html",
                "icon": "fas fa-fw fa-globe",
            }


def dashboardMenu(comm):
    """
    Defines the menu entry corresponding to the "Dashboard" option in the left-menu.
    Args:
        comm: the current context's community object.

    Returns:
        A dictionary containing the sub-menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "dashboard",
                "url": "c/{}/dashboard".format(comm.slug),
                "text": "Dashboard",
                "template": "left_navigation_bar/menu_entry.html",
                "icon": "fas fa-fw fa-tachometer-alt",
            }


def settingsMenu(comm):
    """
    Defines the menu entry corresponding to the "Settings" option in the left-menu.
    Args:
        comm: the current context's community object.

    Returns:
        A dictionary containing the sub-menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "settings-{}".format(comm.slug),
                "url": "community/manage/{}/settings".format(comm.slug),
                "text": "Settings",
                "template": "left_navigation_bar/submenu_entry.html",
                "icon": "fas fa-fw fa-cogs",
            }


def descriptionMenu(comm):
    """
    Defines the menu entry corresponding to the "Description" option in the left-menu.
    Args:
        comm: the current context's community object.

    Returns:
        A dictionary containing the sub-menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "description-{}".format(comm.slug),
                "url": "community/manage/{}/description".format(comm.slug),
                "text": "Description",
                "template": "left_navigation_bar/submenu_entry.html",
                "icon": "fas fa-fw fa-list-alt",
            }


def usersMenu(comm):
    """
    Defines the sub-menu entry corresponding to the "Users" option in the left-menu.
    Args:
        comm: the current context's community object.

    Returns:
        A dictionary containing the sub-menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "users",
                "url": "community/manage/{}/users".format(comm.slug),
                "text": "Users",
                "template": "left_navigation_bar/submenu_entry.html",
                "icon": "fas fa-fw fa-users",
            }


def joinFormMenu(comm):
    """
    Defines the sub-menu entry corresponding to the "Join Form" option in the left-menu.
    Args:
        comm: the current context's community object.

    Returns:
        A dictionary containing the sub-menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "joinform",
                "url": "community/manage/{}/joinform".format(comm.slug),
                "text": "Join Form",
                "template": "left_navigation_bar/submenu_entry.html",
                "icon": "fas fa-fw fa-th-list",
            }


def groupsMenu(comm):
    """
    Defines the sub-menu entry corresponding to the "Groups" option in the left-menu.
    Args:
        comm: the current context's community object.

    Returns:
        A dictionary containing the sub-menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "groups",
                "url": "community/manage/{}/groups".format(comm.slug),
                "text": "Groups",
                "template": "left_navigation_bar/submenu_entry.html",
                "icon": "fas fa-fw fa-object-group",
            }


def componentsMenu(comm):
    """
    Defines the sub-menu entry corresponding to the "Components" option in the left-menu.
    Args:
        comm: the current context's community object.

    Returns:
        A dictionary containing the sub-menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "components",
                "url": "community/manage/{}/components".format(comm.slug),
                "text": "Components",
                "template": "left_navigation_bar/submenu_entry.html",
                "icon": "fas fa-fw fa-puzzle-piece",
            }


def communicationMenu(comm):
    """
    Defines the sub-menu entry corresponding to the "Communication" option in the left-menu.
    Args:
        comm: the current context's community object.

    Returns:
        A dictionary containing the sub-menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "communication",
                "url": "community/manage/{}/communication".format(comm.slug),
                "text": "Communication",
                "template": "left_navigation_bar/submenu_entry.html",
                "icon": "fas fa-fw fa-comment",
            }


def draftsMenu(comm):
    """
    Defines the sub-menu entry corresponding to the "Communication" option in the left-menu.
    Args:
        comm: the current context's community object.

    Returns:
        A dictionary containing the sub-menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "drafts",
                "url": "community/manage/{}/drafts".format(comm.slug),
                "text": "Drafts",
                "template": "left_navigation_bar/submenu_entry.html",
                "icon": "fas fa-fw fa-pen-square",
            }


def viewsMenu(comm, questionnaire):
    """
    Defines the sub-menu entry corresponding to the "Settings" option in the left-menu.
    Args:
        comm: the current context's community object.

    Returns:
        A dictionary containing the sub-menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "views-{}".format(questionnaire.slug),
                "url": "community/manage/{}/q/{}/settings".format(comm.slug, questionnaire.slug),
                "text": "Views",
                "template": "left_navigation_bar/submenu_entry.html",
                "icon": "fas fa-fw fa-window-maximize",
            }


def questionSetsMenu(comm, questionnaire):
    """
    Defines the sub-menu entry corresponding to the "Question Sets" option in the left-menu.
    Args:
        comm: the current context's community object.

    Returns:
        A dictionary containing the sub-menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "qset-"+questionnaire.slug,
                "url": "community/manage/{}/qsets/{}".format(comm.slug, questionnaire.slug),
                "text": "Question Sets",
                "template": "left_navigation_bar/submenu_entry.html",
                "icon": "fas fa-fw fa-list-ol",
            }


def signInMenu():
    """
    Defines the menu entry corresponding to the "Sign In" option in the left-menu.

    Returns:
        A dictionary containing the menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "signin",
                "url": "login",
                "text": "Sign In",
                "template": "left_navigation_bar/menu_entry.html",
                "icon": "fas fa-fw fa-sign-in-alt",
            }


def signOutMenu():
    """
    Defines the menu entry corresponding to the "Sign Out" option in the left-menu.

    Returns:
        A dictionary containing the menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "signout",
                "url": "accounts/signout/",
                "text": "Sign out",
                "template": "left_navigation_bar/menu_entry.html",
                "icon": "fas fa-fw fa-sign-out-alt",
            }


def profileMenu():
    """
    Defines the menu entry corresponding to the "Profile" option in the left-menu.

    Returns:
        A dictionary containing the menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "profile",
                "url": "accounts/profile_edit/",
                "text": "Profile",
                "template": "left_navigation_bar/menu_entry.html",
                "icon": "fas fa-fw fa-user",
            }


def notificationsMenu():
    """
    Defines the menu entry corresponding to the "Notifications" option in the left-menu.

    Returns:
        A dictionary containing the menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "notifications",
                "url": "notifications",
                "text": "News",
                "template": "left_navigation_bar/menu_entry.html",
                "icon": "fas fa-bell",
            }


def jobQueueMenu():
    """
    Defines the menu entry corresponding to the "Job Queue" option in the left-menu.

    Returns:
        A dictionary containing the menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "jobqueue",
                "url": "jobs/list",
                "text": "Job Queue",
                "template": "left_navigation_bar/menu_entry.html",
                "icon": "fas fa-fw fa-list-alt",
            }


def developersMenu():
    """
    Defines the menu entry corresponding to the "Developers" option in the left-menu.

    Returns:
        A dictionary containing the menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "developer",
                "url": "developer",
                "text": "Developers",
                "template": "left_navigation_bar/menu_entry.html",
                "icon": "fas fa-fw fa-code",
            }


def apiMenu(url):
    """
    Defines the menu entry corresponding to the "API Info" option in the left-menu.
    
    Args:
        url: the api menu entry's url.

    Returns:
        A dictionary containing the menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "apiinfo",
                "url": url,
                "text": "API Info",
                "template": "left_navigation_bar/menu_entry.html",
                "icon": "fas fa-fw fa-list-ul",
            }


def adminMenu():
    """
    Defines the menu entry corresponding to the "Admin" option in the left-menu.
    
    Returns:
        A dictionary containing the menu entry with its corresponding attributes to be rendered by the template.

    """
    return {
                "id": "admin",
                "url": "admin",
                "text": "Admin",
                "template": "left_navigation_bar/menu_entry.html",
                "icon": "fas fa-fw fa-cogs",
            }


def importMenu():
    """
    Defines the menu entry corresponding to the "Import" option in the left-menu and its submenus.

    Returns:
        A dictionary containing the menu entry with its corresponding attributes to be rendered by the template. Contains
         also the Import sub-menus "Import Questionnaire" and "Import Fingerprint".

    """
    return {
                "id": "import",
                "url": "",
                "text": "Import",
                "template": "left_navigation_bar/menu_entry.html",
                "icon": "fas fa-fw fa-upload",
                "menu_entry_submenu": [
                    {
                        "id": "import_questionnaire",
                        "url": "questionnaire/import",
                        "text": "Import Questionnaire",
                        "template": "left_navigation_bar/submenu_entry.html",
                        "icon": "",
                    },
                    {
                        "id": "fingerprint",
                        "url": "fingerprint/import",
                        "text": "Import Fingerprint",
                        "template": "left_navigation_bar/submenu_entry.html",
                        "icon": "",
                    }
                ]
            }


def exportMenu():
    """
    Defines the menu entry corresponding to the "Export" option in the left-menu and its submenus.

    Returns:
        A dictionary containing the menu entry with its corresponding attributes to be rendered by the template. Contains
         also the Export sub-menu "Export Questionnaire".

    """
    return {
                "id": "export",
                "url": "",
                "text": "Export",
                "template": "left_navigation_bar/menu_entry.html",
                "icon": "fas fa-fw fa-download",
                "menu_entry_submenu": [
                    {
                        "id": "export_questionnaire",
                        "url": "questionnaire/export",
                        "text": "Export Questionnaire",
                        "template": "left_navigation_bar/submenu_entry.html",
                        "icon": "",
                    }
                ]
            }


def pluginMenu(plugin, url, sublink=False, extLink=False):
    if sublink:
        template = "left_navigation_bar/submenu_entry_plugin.html"
    else:
        template = "left_navigation_bar/menu_entry_plugin.html"
    return {
        "id": "plugin-{}".format(plugin.slug),
        "url": url,
        "text": plugin.name,
        "template": template,
        "image": plugin.icon.url if plugin.icon else "",
        "extLink": extLink
    }


def pluginGroupMenu(pg):
    return {
        "id": "plugin-group-{}".format(pg),
        "url": "",
        "text": pg,
        "template": "left_navigation_bar/menu_entry.html",
        "icon": "fas fa-folder",
        "menu_entry_submenu": []
    }
