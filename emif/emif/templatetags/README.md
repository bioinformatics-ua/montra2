# Left Menu implementation
This readme contains all the information regarding the design and implementation of the left navigation bar(or left menu).

## Table of Contents

1. [How it is implemented](#how-it-is-implemented)
2. [Files structure](#files-structure)
    1. [Left navigation tag](#left-navigation-tag)
        * [Sections](#sections)
        * [Entries](#entries)
    2. [Menu entry tag](#menu-entry-tag)
    3. [Menu entries templates](#menu-entries-templates)
    4. [Official documentation](#official-documentation)
3. [How to edit the left menu](#how-to-edit-the-left-menu)
    1. [Adding new entries](#adding-new-entries)
        * [Using the existing templates](#using-the-existing-templates)
        * [Creating a new template](#creating-a-new-template)
    2. [Removing existing entries for a certain installation](#removing-existing-entries-for-a-certain-installation)
    3. [Editing existing entries](#editing-existing-entries)
4. [Further notes](#further-notes) 

**Disclaimer**: If you just want to edit the current menu, go directly to the section [*How to edit the left menu*](#how-to-edit-the-left-menu). Nonetheless, it is advised to read the full documentation.

## How it is implemented
The implementation is based on django's template, the visuals are dealt with in CSS and some logic is built using JavaScript, more specifically with the library jQuery. Detailes are provided below.

The templates are HTML files that contain the desired static output. Additionally, they rely in special objects called "contexts" that are provided by django's views (views.py files). Contexts contain information about the current active menu, the current user, among others. These template files are usually located in folders called "templates" under each app's directory (i.e. the templates for the left menu exist under the directory emif/emif/templates/left_navigation_bar).

Moreover, templates may contain special syntax in the form of "tags". These tags are "designed to address the presentation logic needs of your application" and django already provides a variety of them to serve the most common use cases (i.e. the tag "if/else/endif" allows the creation of an if conditional inside the template). Nonetheless, django also give the developers the possibility to create custom tags. These tags are Python files where the developer can define a set of instructions that will be executed before rendering the template. In this case, the left navigation tags exist under the emif/emif/templatetags/left_menu_tags.py. In this file, all the menu logic and processing is implemented. This way, all the logic regarding the left menu - like what should be shown and that should not - is executed in the server-side instead of the client.

Before continuing, it is important to understand the definition of an "entry". In the left menu, an "entry" is any button or text that are displayed to the user. This could be a menu entry, sub-menu entry or just section texts. The definition is abstract to allow the menu to be easily extended, as detailed below.

## Files structure
**All the tags that are mentioned next are implemented in the emif/emif/templatetags/left_menu_tags.py file**

This section contains the information regarding the file structure for defining tags and how each tag is conceptually designed and implemented. 

### Left navigation tag
The main template for the system is located in the emif/base.html file. The left menu is loaded in this template using a custom tag called left_navigation_bar (loaded as `{% left_navigation_bar %}`). This is the main tag that contains all the processing of the left menu. This tag is registered under the method with the same name and the decorator `register.inclusion.tag` takes two special parameters: the template file (HTML) corresponding to this tag and the parameter `takes_context=True`. This way, when this tag is used (as in the base.html file) the tag's body is executed and, finally, the template is rendered. The second parameter allows the context that is passed from the views to the template to be available inside the custom tag. 

Inside this tag the developer may adjust the left menu logic. I.e., if the user is not authenticated, the sign-in entry is displayed while others, such as the catalogue, are not even shown because the user is anonymous. The design is divided in two parts: logic and button rendering.  

#### Sections
In the parent's method `left_navigation_bar()`, the sections are added by extending the list `listed_menu_entries`. Therefore, to add a section the developer must extend the previously mentioned list with the desired section. Each section contains a set of menu entries, both buttons and headings. <br>
In order to display a menu entry, it must be associated with a section. In example, the "FAQ" entry is under the "Portal" section (method `portal()`).  Each menu entry's logic is then defined under its corresponding section. In example, the "FAQ" entry is added under the "Portal" section as follows:
```
def portal(request):
    if config.faqMenu:
        menus.extend([faqMenu()])
```
Entries are enable/disabled by editing the `settings.py` file under the `CONSTANCE_CONFIG` dictionary. 

```
CONSTANCE_CONFIG = {
 'faqMenu':(True, 'This option shows the button in the section Portal of the left menu')
 }
```

Each section's logic is defined in its own method. I.e., the "Catalogue" section contains a set of entries that allow the user to interact with several functionalities of the system regarding the catalogue's browsing, editing, etc. Moreover, the catalogue is designed in different ways depending on the installation type and other factors. Therefore, the `catalogue()` method defines this logic and decides which entries should be displayed to the current user. This logic is followed by most of the sections in the left menu. Note that some entries, such as the "Catalogue", contain sub-menus under it.

#### Entries
Lastly, each button that the user sees in the left menu are defined in their own methods. In example, the "FAQ" entry has its method `faqMenu` that contains all the information that will be used to render the "FAQ" button. **All the buttons must return a dictionary containing the information needed by the button**. In example, the "FAQ" button looks as follows:

```
def faqMenu():
    return {
                "id": "faq",
                "url": "faq",
                "text": "FAQ",
                "template": "left_navigation_bar/menu_entry.html",
                "icon": "fas fa-fw fa-question-circle",
            }
```
            
* The `id` key is used to highlight the current active menu (or sub-menu). This must match the `activemenu`  or `activesubmenu` from the context passed in the `views.py` file. Otherwise, the entry will not be visually highlighted when selected.
* The `url`key is passed to the button's `href` attribute.
* The `text`key defines the  string that will be shown in the button.
* The `template` key defines the HTML template file corresponding to the button. This will be detailed below.
* The `icon`key defines the icon that is associated to the button.

On the other hand, in order to implement sub-menus the developer must associate the sub-menu entries to a menu entry. I.e., the "Contact" menu entry contains two sub-menu entries: "Bug Report" and "Feedback". Therefore, the "Contact" entry and its sub-menus are implemented as follows:

```
def contactMenu():
    return {
                "id": "contact",
                "url": "",
                "text": "Contact",
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
                        "id": "feedback",
                        "url": "feedback",
                        "text": "Feedback",
                        "template": "left_navigation_bar/submenu_entry.html",
                        "icon": "fas fa-fw fa-info",
                    }
                ]
            }
```

Since the menu-entry contains a key `menu_entry_submenu`, these entries will be detected in the `menu_entry.html` template and they will be rendered accordingly. It is to note that each sub-menu entry is also a dictionary, similar to the menu-entry, but with a small difference: the `template` value is "left_navigation_bar/submenu_entry.html". 

 ### Menu entry tag
Alongisde the `left_navigation_bar` tag, there is also a `menu_entry` tag. Its logic is not as complex as the previous, but it plays an important role in the abstract definition of a menu entry. Firstly, it is to be noted that it is associated with the `left_navigation_bar/menu_object.html` which does not contain a lot of code in it. It simply extends the passed template using the tag `{% extends template %}`. This allows the usage of *any* template for an entry generated by the custom tag. This is particularly useful since the developer can re-use as much code as desired and has the flexibility to use any template for any entry as needed. 

### Menu entries templates
As seen previously, each entry on the left menu is defined on the server side. This allows that each entry follows an abstract definition, allowing the developer to decide which template should be used for each menu entry. I.e, in the "FAQ" example the `left_navigation_bar/menu_entry.html` template is to be used. But, on other situations, other templates are needed such as the `left_navigation_bar/submenu_entry.html`. Nonetheless, any other could be used. 

Currrently, five templates are defined:

* `menu_entry.html` - defines the visual output of a menu entry.
* `menu_heading.html` - defines the visual output of a menu heading. These are simple templates containing only a `<span>` containing some text. They allow the user to insert text in the left-menu to separate sections.  
* `submenu_entry.html` - defines the visual output of a sub-menu entry.
* `submenu_heading.html`- defines the visual output of a submenu heading. 
* `menu_entry_notifications.html`- defines the visual output of the "Notifications" entry. This is similar to a menu entry, almost identical, but allows the user to define entries that contain a small baloon next to the entry's menu containing the number of unread notifications.

### Official documentation
You can find the official documentation followed during the implementation in the following links:

* [Django templates - main documentation](https://docs.djangoproject.com/en/3.0/ref/templates/language/)
* [Django templates - custom tags](https://docs.djangoproject.com/en/3.0/howto/custom-template-tags/)
* [Django templates - performance tips](https://docs.djangoproject.com/en/3.0/topics/performance/)


## How to edit the left menu
This section will guide you, the developer, through the process of editing the left menu. For each case, a dummy case will be given that must be adapted to the user's needs.

### Adding new entries
In order to add new entries in the left menu, whether they are menu entries, headings or sub-menus, it is advised to follow the given instructions. <br>
Let's create a button with the text "My Button - username" with the url "/mybutton" where `username` is the current user's username. This button is a menu entry, that is, it is not a sub-menu entry. Moreover, this entry does not contain any children (i.e. sub-menus). Lastly, this entry will be displayed under the entry "About" in the section "Portal".

#### Using the existing templates
The button will have the same visual output as the one defined in the template `left_navigation_bar/menu_entry.html`. <br>
Edit the file `left_menu_tags.py` and add the following code:

1. Create the entry's method. Let's say this method is called `myButton(user)` and receives one input parameter `user`. Nonetheless, you can add the parameters that you see fit in order to make your button work (such as the community, questionnaire, or any other element that you might need). Most of these parameters are already defined in the parent's method `left_navigation_bar()`. This method should return a dictionary containing the button's attributes, as described previously. This method should look as follows:
```
def myButton(user):
    return {
                "id": "mybutton",
                "url": "mybutton",
                "text": "My Button - {}".format(user.username),
                "template": "left_navigation_bar/menu_entry.html",
                "icon": "fas fa-fw fa-question-circle",  # or any other icon that you desire
            }
```

2. Add your button next to the "About" section by editing the "Portal" method (`portal()`).
If you wish your button to be removable, you must also edit the `settings.py` file and add a boolean variable that controls whether your button should be, or not, displayed. Add the following variable to the `CONSTANCE_CONFIG` dictionary, next to the left menu options:
```
'myMenu': (True, 'This is my menu and I want it to be displayed!')
```
Finally, to add your button to the left menu extend the list containing the "Portal" entries as follows, next to the `about` entry:
```
def portal():
    menus = [portalSection()]  # Initialize the menus list with a header that displays the string "Portal"
    if config.aboutMenu:
        menus.extend([aboutMenu()])
    if config.myMenu:  # This is your variable defined in the settings.py file
        menus.extend([myButton(request.user)])  # This is your button's method
```
You can easily disable your button by changing the variable `myMenu` value to `False`.
There are two things to note here: if you want your menu entry to have sub-menus, you must follow a similar pattern as described previously. Also, you might want to use other template than the one defined in `menu_entry.html`. You can change this, as explained next. 

#### Creating a new template
First of all, it is to note that  the process to add your menu entry is the same as described previously. The main difference is that you must create a template to have the visual output that you desire and you must pass it's path in the `template` key in the dictionary returned by your entry's method.
1. Create a template called `my_button_template.html` and place it under the directory `montra-pvt/emif/emif/templates/left_navigation_bar`. Even though it is not mandatory to use this directory, it is recommended to use it since the file hierarchy is cleaner and easier to browse and understand.
2. In your method `myButton(user)` pass the new template as follows:
```
def myButton(user):
    return {
                "id": "mybutton",
                "url": "mybutton",
                "text": "My Button - {}".format(user.username),
                "template": "left_navigation_bar/my_button_template.html", # Note that the new template is passed.
                "icon": "fas fa-fw fa-question-circle",  # or any other icon that you desire
            }
```
**Note**: This is a simple case where your entry is just under the "Portal" section and it does not have a lot of logic associated to it. If there are other constraints that affect whether the button should be, or not, displayed you need to place it before the extension of the `menus` list. As follows (pseudo-code):
```
def portal():
    menus = [portalSection()] 
    if myCondition:
        if config.myMenu:
            menus.extend([myButton(request.user)])
```

### Removing existing entries for a certain installation
In order to remove an existing entry, you just need to edit the `settings.py` file and change the entry's value to `False`. If using the Django's admin page, simply uncheck the entry that you wish to remove. <br>
If you desire to completely remove the entry in the code, you can remove the lines where the `menus` list is extended with your entry.  

### Editing existing entries
While editing an entry, you might desire to either change the button's logic or its appearance (as changing the template or the icon).
1. If you desire to change the logic that decides whether the button should be displayed, edit the line where the `menus` list is extended.
```
def portal():
    menus = [portalSection()] 
    if myNewCondition:
        if config.myMenu:
            menus.extend([myButton(request.user)])
```
2. In the other hand, if you desire to change its visual then you must edit the entry's method. Let's say you want to edit the button's text. Then, edit the `myButton()` method as follows:
```
def myButton(user):
    return {
                "id": "mybutton",
                "url": "mybutton",
                "text": "My Button - New Text",  # Note that the text is edited
                "template": "left_navigation_bar/my_button_template.html", 
                "icon": "fas fa-fw fa-question-circle", 
            }
```

## Further notes
The order on which the menu entries are displayed is the same as the one that they have in the `menus` list. That is, if the entryA comes before the entryB then the first should appear before the latter in the `menus` list.
```
menus.extend([entryA])  # Entry A comes first
menus.extend([entryB])
>>> menus
>>> [entryA, entryB]
```
The same rational is applied to sections. In the parent's method `left_navigation_bar()`, the sections are added by extending the list `listed_menu_entries`.
