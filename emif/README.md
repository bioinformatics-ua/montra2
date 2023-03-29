# Technical Documentation 
==========================================

## Package structure

- accounts: all user management, signin, signup here.
- achilles: achilles plugin is contained here; it is also served by the same application engine.
- advancedsearch: Advanced Search lives here 
- api: our public methods API should be defined here. It will re-use other apis for other applications like for instance, community.api.py ;  TBD: we want to centralize in this app an API for javascript - so the idea will be create the Services and Javascript Client. 
- community: all management of communities, groups and roles 
- compare: related with comparison of entries (diff)
- control_version: to connect github and check pending issues and also to report bugs.
- dashboard: the code for community dashboard. TBD: we need a refresh and make it useful.
- datatable: Matrix View services (see in Community, left hand side Custom View)
- developer: all microkernel architecture is supported by this package. Here, there are the developer panel, you can write javascript plugins in a web interface and all the core are supported here. 
- docs_manager: package related to the upload of database and community documents.
- fingerprint - it is support the main entity "New Entry". In the past it was known as database or fingerprint. Now it is an entry. It is an instance of the questionnaire and links with everything. 
- fixtures: package with some data to load at bootstrap.
- geolocation: package related with map and points of each entry in the map
- literature: application to support literature plugin and also related publications
- media - just files and directories to store media files
- notifications: application to deal with notification between users and databases 
- population_characteristics: Jerboa Plugin Services, also know as Sustentability J or Population Characteristics. Nice source of charts.
- public: share public link with an entry, the code are here. For instance, create a public link for a specific entry. 
- questionnaire: very important app, here are supported questionnaire, the renders for each type of questions, templates for them, import excel with questions and export, etc.
- searchengine - the searchengine are centralized here
- security - package to deal with security staff, such as recaptacha
- statistics - package to calculate some statistics
- studies - package for the 'study requests' management
- taskqueue - we support async tasks in UI, and this package deals with that. For instance, import questionnaire or download heavy date. Are just processed in background. It supports all tasks structure. 
- tag: code for autocompletion 
- utils: just random scripts and misc code 


## Convenctions 

### Python 

For each package, it always should have:
- api.py - to specify all web services 
- services.py - to provide core logic of each services.


### Javascript/CSS

All javacript should be in:
- static/js 
- static/css 

#### How to build a new page

Template: 
For now, we do not have a single page view and we rely on django templates.

Nevertheless, for forms, do not use full reload page. Let's try to make always javascript controllers and service to ajax.

Javascript: 

Example:

- static/js/<modulename>.services.js
- static/js/<modulename>.controllers.js


Or for big apps:


- static/js/<modulename>/services/example1.js
- static/js/<modulename>/controllers/exampleComp1.js


##### Controller 

In html, you can use custom html fields inside your html tag, such as:

- m-click="update('elem_{{elem.0.id}}', '{{elem.1}}')" 
- m-submit="reset()" 

Some examples: 

```
<button m-submit="reset()" type="reset" class="btn btn-default pull-right">Revert Changes</button>
```


Example:



```
function UserGroupsPluginComponent() {
    this.container = $('.user-groups-plugins-container');
    this.values = {};
};
UserGroupsPluginComponent.prototype.init = function () {
    var self = this;

    // Bind the events for all the checkboxes 
    this.container.find('[m-click]').each(function () {
        var $element = $(this);
        var functionCall = $element.attr('m-click');

        $element.off('click tap');
        $element.on('click tap', function (event) {



        });
        $element.on('change', function (event) {

            var $target = $(event.target);
            var tag = $target.prop('name');
            var checked = $target.prop('checked');
            var elem = tag.split(" ")[0];
            var email = tag.split(" ")[1];
            self.update(elem, email, checked);
        });
    });
    // Bind the events for reset and save @ server
    this.container.find('[m-submit]').each(function () {

        var $element = $(this);
        var functionCall = $element.attr('m-submit');
        $element.off('click tap');
        $element.off('change');
        $element.on('click tap', function (event) {
            if (event.preventDefault())
                event.preventDefault();
            if (event.stopPropagation())
                event.stopPropagation();
            if (event.stopImmediatePropagation())
                event.stopImmediatePropagation();
            // Example
            eval("self." + functionCall);


        });
    });
};

// Destroy not needed component 
UserGroupsPluginComponent.prototype.destroy = function () {
    this.container = null;
    this.values = null;
};
// Update for server
UserGroupsPluginComponent.prototype.update = function (element, emailElement, valueElement) {
    if (this.values[element]===undefined){
        this.values[element] = [];
        this.values[element].push({email: emailElement, value: valueElement});
    }
    else{
        this.values[element].push({email: emailElement, value: valueElement});
    };
};

// Reset for the last state
UserGroupsPluginComponent.prototype.reset = function () {
    this.values = {};
    window.location.reload();
};
// Save to  Server.
UserGroupsPluginComponent.prototype.save = function () {
    var service = new UserGroupsPluginService(MontraAPI.getBase() + "community/" + MontraAPI.getCurrentCommunitySlug() + "/");
    service.submit(this.values, function () {
        bootbox.alert({
            message: "Saved with success.",
            backdrop: true
        });
    }, function () {
        bootbox.alert({
            message: "Error: it was unable to save this changes",
            backdrop: true
        });
    });
};
```


##### Services 

Example here: 


```

function UserGroupsPluginService(baseUrl) {
    this.url = baseUrl + "api/user/groups";

};
// Initial all endpoints
UserGroupsPluginService.prototype.init = function (baseUrl) {
    this.url = baseUrl + "api/user/groups";
};

// Add the communications mechanisms to submit new update values
UserGroupsPluginService.prototype.submit = function (values, successFn, failFn) {

    $.ajax({
        url: this.url,
        type: "POST",
        dataType: "json",
        data: JSON.stringify({data: values}),
        contentType: "application/json; charset=utf-8",
        traditional: true,
    })
        .done(function (e) {
            successFn();
        })
        .fail(function (e) {
            failFn();
        });
};


````


#### Montra API 

There are a few methods that you can use, and the idea will be grow this API and developers module. 

- MontraAPI.getBase()
- MontraAPI.getCurrentCommunitySlug() 


#### Reverse Django URLs to Javascript

You can reverse urls from django to javascript simple like that:

```
Urls['manage-groups-community']('ria')
``` 

It will retrieve: 

```
/community/ria/api/groups
```

To update routes:

```
python manage.py collectstatic_js_reverse
```


#### Where should we extend Montra Framework and API?

First, you are strongly invited to improve montra framework. 

We should use the following files:

- api/static/montra.api.js
- api/static/montra.utils.js
- api/static/montra.framework.js

