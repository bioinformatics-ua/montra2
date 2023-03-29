$(function () {
    var timer;
    var __delay = function (callback, ms) {
        clearTimeout(timer);
        timer = setTimeout(callback, ms);
    };
    var valid_name;
    var valid_type;
    var setSave = function () {
        var save_button = $('#save-plugin');

        if (valid_type && valid_name)
            save_button.removeAttr('disabled');
        else
            save_button.attr('disabled', 'disabled');

    };
    var iconChanger = function (target, status) {
        var icon = $(target);

        switch (status) {
            case 'load':
                icon.html('<i class="fas fa-fw fa-refresh fa-1x fa-spin text-info"></i>');
                break;
            case 'success':
                icon.html('<i title="The value is valid, and can be used." class="fas fa-fw fa-check fa-1x text-success"></i>');
                break;
            case 'warn':
                icon.html('<i title="The name is already taken. Please choose another" class="tooltippable fa fa-1x fa-times text-error"></i>');
                break;
            case 'fail':
                icon.html('<i title="The value is invalid." class="tooltippable fa fa-1x fa-times text-error"></i>');
                break;
        }
        icon.tooltip({ container: 'body' });
    };
    var tryType = function (self) {
        var choosen = parseInt($(self).val());
        switch (choosen) {
            case -1:
                valid_type = false;
                iconChanger('#id-type-icon', 'fail'); break;
            default:
                valid_type = true;
                iconChanger('#id-type-icon', 'success'); break;
        }
    };
    $('#id-type').change(function () { tryType(this) });

    var tryIndex = function (self) {
        var chosen = parseInt($(self).val());
        if ((chosen >= 1000) || (chosen < 0)){
            valid_type = false;
            iconChanger('#id-index-icon', 'fail')
        } else {
            valid_type = true;
            iconChanger('#id-index-icon', 'success')
        }
    };
    
    $('#id-index').change(function() { tryIndex(this) });

    $('#id-group-index').change(function() { tryIndex(this) });

    var tryName = function (self) {
        var temptive_name = $(self).val();

        var slug = $('#current_slug').val();

        iconChanger('#id-name-icon', 'load');

        $.post('developer/checkname/', {
            name: temptive_name,
            slug: slug
        })
            .done(function (result) {
                if (result.success) {
                    valid_name = true;
                    iconChanger('#id-name-icon', 'success');
                }
                else {
                    valid_name = false;
                    iconChanger('#id-name-icon', 'warn');
                }

            })
            .fail(function () {
                valid_name = false;
                iconChanger('#id-name-icon', 'warn');
            });

    };

    $('#id-name').keyup(function () {
        __delay(tryName(this), 700);
    });
    $('#id-name').change(function () {
        __delay(tryName(this), 700);
    });


    var tryMenu = function(self) {
        chosen = $(self).val()

        var submenuChildren = $('#leftSubmenuList').children()

        console.log(submenuChildren)

        var flag = false
        for(let i = 0; i < submenuChildren.length && !flag; i++){
            flag = submenuChildren[i].value === chosen || chosen === "";
        }

        if (flag) {
            $('#id-group-icon').html('<i title="The value is valid, and can be used." class="fas fa-fw fa-check fa-1x text-success"></i>') 
        } else {
            $('#id-group-icon').html('<i title="You\'ll be creating a new group" class="fa fa-exclamation-triangle text-warning" aria-hidden="true"></i>')
        }
    }

    $('#submenu').change(function () { tryMenu(this) })

    $('#save_plugin').submit(function (event) {
        var type = parseInt($('#id-type').val());
        var name = $('#id-name').val();
        var index = $('#id-index').val();
        var group_index = $('#id-group-index').val();
        var group = $('#submenu').val();
        var iframe_view = $('input[name=iframe_type]:checked', '#save_plugin').val();
        if (valid_name == undefined) {
            tryName($('#id-name'));
        }
        if (valid_type == undefined) {
            tryType($('#id-type'));
        }

        if (!valid_name || !valid_type) {
            event.preventDefault();

            bootbox.alert('Please confirm if the information filled is valid');
            return false;
        }
    });



    $('#versions').dataTable({
        "bFilter": false,
        "oLanguage": {
            "sEmptyTable": "No versions found for this plugin"
        },
        "order": [[0, "desc"]]
    });

    $("div.toolbar").html('');

    $('#id-name').keyup();
    $('#id-type').change();

    $(document).on('change', '.btn-file :file', function () {
        var input = $(this),
            numFiles = input.get(0).files ? input.get(0).files.length : 1,
            label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
        input.trigger('fileselect', [numFiles, label]);
    });

    $(document).ready(function () {
        $('.btn-file :file').on('fileselect', function (event, numFiles, label) {

            var input = $(this).parents('.input-group').find(':text'),
                log = numFiles > 1 ? numFiles + ' files selected' : label;

            if (input.length) {
                input.val(log);
            } else {
                if (log) alert(log);
            }

        });
    });

    {
        const remove_icon_checkbox = document.getElementById("remove-icon-checkbox");
        if (remove_icon_checkbox) {
            const image_uploader = document.getElementById("depuploader");
            remove_icon_checkbox.onchange = event => {
                image_uploader.disabled = event.target.checked;
            }
        }
    }
});
