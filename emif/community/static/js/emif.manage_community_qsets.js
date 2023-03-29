

/******************************************************** 
 * Support the interaction with server 
 *********************************************************/


function GroupsQSetsService(baseUrl) {
    this.url = baseUrl + "api/qsets";

};
// Initial all endpoints
GroupsQSetsService.prototype.init = function (baseUrl) {
    this.url = baseUrl + "api/qsets";
};

// Add the communications mechanisms to submit new update values
GroupsQSetsService.prototype.submit = function (values, successFn, failFn) {

    $.ajax({
        url: this.url,
        type: "POST",
        dataType: "json",
        data: values,
        //data: JSON.stringify({data: values}),
        //contentType: "application/json; charset=utf-8",
        //traditional: true,
    })
        .done(function (e) {
            successFn();
        })
        .fail(function (e) {
            failFn();
        });
};

/****************************************************
 *  Component to Groups QSets 
 ****************************************************/

function GroupsQSetsComponent() {
    this.container = $('.groups-qsets-container');
    this.values = {};
};
GroupsQSetsComponent.prototype.init = function () {
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

            console.log("GroupsQSetComponent Values: ");
            console.log(self.values);

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

// Destroy not needed component 
GroupsQSetsComponent.prototype.destroy = function () {
    this.container = null;
    this.values = null;
};
// Update for server
GroupsQSetsComponent.prototype.update = function (element, value) {
    this.values[element] = value;
};

// Reset for the last state
GroupsQSetsComponent.prototype.reset = function () {
    this.values = {};
    window.location.reload();
};
// Save to  Server.
GroupsQSetsComponent.prototype.save = function () {
    var service = new GroupsQSetsService(MontraAPI.getBase() + "community/" + MontraAPI.getCurrentCommunitySlug() + "/");
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
    var groupsQSetsComponent = new GroupsQSetsComponent();
    groupsQSetsComponent.init();
});

$(document).ready(function () {
    $('#groups_qsets').DataTable(
        {
            //"aaSorting" : [[]],
            "bSort": true,
            "columnDefs": [
                { targets: 0, "orderable": true },
                { targets: '_all', "orderable": false }
            ]
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