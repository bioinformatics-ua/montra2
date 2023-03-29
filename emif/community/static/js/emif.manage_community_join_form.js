

function addJoinFormQuestion() {
    var bd = bootbox.dialog({
        title: 'Add Community Join Form Question',
        message: '<div id="addquestion">\
        <div class="form-group">\
        <label for="question_text">Question:</label>\
        <input id="question_text" placeholder="Please introduce the question" type="text" class="form-control" />\
        <label for="question_required">Required:</label>\
        <input id="question_required" type="checkbox" checked />\
        </div>\
        </div>',
        buttons: {
            success: {
                label: "Add",
                className: "btn-success",
                callback: function () {
                    const name = $('#question_text').val();

                    if (name && name.length > 0) {
                        $('#qadd').val(name);
                        if ($("#question_required").is(":checked")) {
                            $("#qrequired").val("yes")
                        }
                        else {
                            $("#qrequired").val("no")
                        }

                        bd.modal('hide');
                        $('#question_add').submit();

                        if (window.history) {
                            window.history.replaceState(null, null, window.location.href);
                        }
                    }
                }
            }
        }
    });
}
