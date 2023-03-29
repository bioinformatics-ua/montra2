

/******************************************************** 
 * Support the interaction with server 
 *********************************************************/

function GroupsPluginService(baseUrl) {
    this.url = baseUrl + "api/groups";

};
// Initial all endpoints
GroupsPluginService.prototype.init = function (baseUrl) {
    this.url = baseUrl + "api/groups";
};

// Add the communications mechanisms to submit new update values
GroupsPluginService.prototype.submit = function (values, successFn, failFn) {

    $.ajax({
        url: this.url,
        type: "POST",
        dataType: "json",
        data: values
    })
        .done(function (e) {
            successFn();
        })
        .fail(function (e) {
            failFn();
        });
};


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






/****************************************************
 *  Component to Groups Plugin 
 ****************************************************/

function GroupsPluginComponent(module) {
    this.container = $('.groups-plugins-container');
    this.values = {};
    Controller.call(this, module, new View(this));

};
extend(GroupsPluginComponent, Controller);


GroupsPluginComponent.prototype.init = function () {
    var self = this;

    // Bind the events for all the checkboxes 
    this.container.find('[m-click]').each(function () {
        var $element = $(this);
        var functionCall = $element.attr('m-click');

        $element.off('click tap');
        $element.on('click tap', function (event) {
            var $target = $(event.target);
            var tag = $target.prop('name');
            var checked = $target.prop('checked');

            self.update(tag, checked);
        });
    });
    // Bind the events for reset and save @ server
    this.container.find('[m-submit]').each(function () {

        var $element = $(this);
        var functionCall = $element.attr('m-submit');
        $element.off('click tap');
        $element.on('click tap', function (event) {
            if (event.preventDefault())
                event.preventDefault();
            if (event.stopPropagation())
                event.stopPropagation();
            if (event.stopImmediatePropagation())
                event.stopImmediatePropagation();

            eval("self." + functionCall);

        });


    });
};

GroupsPluginComponent.prototype.initialize = function () {
    this.init();
};

// Destroy not needed component 
GroupsPluginComponent.prototype.destroy = function () {
    this.container = null;
    this.values = null;
};
// Update for server
GroupsPluginComponent.prototype.update = function (element, value) {
    this.values[element] = value;
};

// Reset for the last state
GroupsPluginComponent.prototype.reset = function () {
    this.values = {};
    window.location.reload();
};
// Save to  Server.
GroupsPluginComponent.prototype.save = function () {
    var service = new GroupsPluginService(MontraAPI.getBase() + "community/" + MontraAPI.getCurrentCommunitySlug() + "/");
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



/****************************************************
 *  Component to User Groups Plugin 
 ****************************************************/



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
        // Before inserting the action on the this.values array, let's check if it already
        //  has a value associated with the given user. If it has, update it, avoiding to have
        //  several actions for the same users
        for (const user_object of this.values[element]) {
            if (user_object.email === emailElement) {
                user_object.value = valueElement;
                return;
            }
        }
        this.values[element].push({email: emailElement, value: valueElement});
    }
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



$(function () {
    var groupsPluginComponent = new GroupsPluginComponent();
    groupsPluginComponent.init();
    var userGroupsPluginComponent = new UserGroupsPluginComponent();
    userGroupsPluginComponent.init();


});

$(document).ready(function () {

    $('#groups_plugins').DataTable(
        {
            //"aaSorting" : [[]],
            "bSort": true,
            "columnDefs": [
                { targets: 0, "orderable": true },
                { targets: '_all', "orderable": false }
            ]
        }
    );
//#TO REMOVE, moved to the other ..qsets.js file
// $('#groups_qsets').DataTable(
//   {
//     //"aaSorting" : [[]],
//     "bSort" : true,
//     "columnDefs": [
//       { targets: 0, "orderable": true },
//       { targets: '_all', "orderable": false }
//     ]
//   }
//     );

    $('#groups_and_users').dataTable(
        {
            "bSort": true,
            "columnDefs": [
                { targets: [0, 1, 2], "orderable": true },
                { targets: '_all', "orderable": false }
            ],
            aLengthMenu: [
                [10, 25, 50, 100, 200, -1],
                [10, 25, 50, 100, 200, "All"]
            ],
            iDisplayLength: -1
        }
    );

});

function check_c(checkbox, col) {
    var val = false;
    if (checkbox.checked) val = true

    checkboxes = document.getElementsByClassName(col);
    for (var i = 0; i < checkboxes.length; i++) {
        checkboxes[i].checked = val;
        var event = document.createEvent("HTMLEvents");
        event.initEvent("change", true, true);
        checkboxes[i].dispatchEvent(event);
    }

}

function getUsers(comm, id) {
    $.get('community/list/' + comm + '/' + id)
        .done(function (data) {
            var content = '';

            content += '<select id="ugop" class="form-control">\
                <option val="-1">-- Add a new user to group</option>';

            for (var i = 0; i < data.possible.length; i++) {
                var member = data.possible[i];
                var mname;
                if (member['first_name']) {
                    mname = member['first_name'] + ' ' + member['last_name']
                } else {
                    mname = member['email']
                }
                content += '<option value="' + member.email + '">' + mname + '</option>'
            }

            content += '</select><button onClick="addUserGroup(\'' + comm + '\', ' + id + ');" class="btn btn-block btn-success">Add</button>';

            content += '<table class="table table-bordered"><tr><th>Name</th><th style="width: 72px;">Manage</th></tr>';
            if (data.members) {
                for (var i = 0; i < data.members.length; i++) {
                    var member = data.members[i];

                    var mname;
                    if (member['first_name']) {
                        mname = member['first_name'] + ' ' + member['last_name']
                    } else {
                        mname = member['email']
                    }

                    content += '<tr><td class="lastuser_tooltip">' + mname + '</td><td>\
                    <button onClick="delUserGroup(\''+ comm + '\', ' + id + ',\'' + member['email'] + '\');" class="btn btn-danger"><i class="fas fa-fw fa-times"></i></button>\
                    </td></tr>';
                }
            }
            if (data.members.length == 0) {
                content += '<tr><td colspan="2"><center>There are currently no members on this group.</center></td></tr>'
            }
            content += '</table>';

            $('#ucontainer').html(content);

        })
        .fail(function () {
            $('#ucontainer').text('Error loading user list, please try again later.');
        });
}
function manageUsers(comm, id) {
    bootbox.dialog({
        title: 'Manage Group Users',
        message: '<div id="ucontainer"><h4><center>Loading, please wait...</center></h4></div>'
    });

    getUsers(comm, id);
}

function addGroup() {
    var bd = bootbox.dialog({
        title: 'Add Community Group',
        message: '<div id="addgroup">\
        <div class="form-group">\
        <label>Name:</label>\
        <input id="gname" placeholder="Please introduce the new group name" type="text" class="form-control" />\
        </div>\
        </div>',
        buttons: {
            success: {
                label: "Add",
                className: "btn-success",
                callback: function () {
                    var name = $('#gname').val();

                    if (name && name.length > 0) {
                        $('#gadd').val(name);
                        bd.modal('hide');
                        $('#gname_add').submit();

                    }

                }
            }
        }
    });
}

function addUserGroup(comm, id) {
    var ug = $('#ugop').val();
    if (ug !== '-1') {

        $.get('community/listadd/' + comm + '/' + id + '/' + ug)
            .done(function (data) {
                if (data.success) {
                    getUsers(comm, id);
                } else {
                    bootbox.alert('Error adding user please try again later.');
                }

            })
            .fail(function () {
                bootbox.alert('Error adding user please try again later.');
            });


    }
}

function delUserGroup(comm, id, email) {
    if (email !== '-1') {

        $.get('community/listdel/' + comm + '/' + id + '/' + email)
            .done(function (data) {
                if (data.success) {
                    getUsers(comm, id);
                } else {
                    bootbox.alert('Error removing user please try again later.');
                }

            })
            .fail(function () {
                bootbox.alert('Error removing user please try again later.');
            });


    }
}
