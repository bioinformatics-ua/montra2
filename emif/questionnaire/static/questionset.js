/*
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
*/
var qvalues = new Array(); // used as dictionary
var qtriggers = new Array();

var depmaps = {};

var active_qset;

function dep_check(expr) {
    expr = expr.split('{')[0];

    var exprs = expr.split(/,(.+)/);
    var qnum = exprs[0];
    var value = exprs[1];

    var qvalue = qvalues[qnum];
    if (value.substring(0, 1) == "!") {
        var multiple_option = qvalues[qnum + '_' + value.substring(1)];
        if (multiple_option != undefined)
            return !multiple_option;
        value = value.substring(1);
        return qvalue != value;
    }
    if (value.substring(0, 1) == "<") {
        qvalue = parseInt(qvalue);
        if (value.substring(1, 2) == "=") {
            value = parseInt(value.substring(2));
            return qvalue <= value;
        }
        value = parseInt(value.substring(1));
        return qvalue < value;
    }
    if (value.substring(0, 1) == ">") {
        qvalue = parseInt(qvalue);
        if (value.substring(1, 2) == "=") {
            value = parseInt(value.substring(2));
            return qvalue >= value;
        }
        value = parseInt(value.substring(1));
        return qvalue > value;
    }
    var multiple_option = qvalues[qnum + '_' + value];
    if (multiple_option != undefined) {
        return multiple_option;
    }
    if (qvalues[qnum] == value) {
        return true;
    }
    return false;
}

function collapseAll(element, div_id) {
    if (element.text().indexOf('Collapse') !== -1) {
        console.log('Collapse all');
        element.text('Expand all');
        if (!element.hasClass('disabled')) {
            element.parents().find('#' + div_id + ' .collapse').each(function(index) {
                $(this).addClass('in');
                $(this).collapse('hide');
            });
        }
    } else {
        console.log('Expand all');
        element.text('Collapse all');
        if (!element.hasClass('disabled')) {
            element.parents().find('#' + div_id + ' .collapse').each(function(index) {
                $(this).removeClass('in');
                $(this).collapse('show');
            });
        }
    }
};

function getChecksAttr(obj) {
    /* while most browser consider getAttributes a function, IE 9< considers it a object
     * So its actually better to use jquery for this
    return obj.getAttribute('checks'); */
    var $obj = $(obj);
    return $obj.attr('checks');
}

function statusChanged(obj, res) {

    if (obj.tagName == 'DIV') {
        obj.style.display = !res ? 'none' : 'block';
        return;
    }
    //obj.style.backgroundColor = !res ? "#eee" : "#fff";
    obj.disabled = !res;
}

function clearcheck(id) {
    console.warn('clearcheck ID: ' + id);
    $(':input[name="' + id + '"]').removeAttr('checked');
    //$(':input[name="'+id+'"]').click();
}

// Track if a question's answer has changed its value
function valchanged(qnum, value, self) {
    if (!(typeof bool_container === 'undefined')) {
        var $self = $(self);

        var just_number = qnum.split('_')[1];
        var clean = qnum.replace('question_', '').replace(/(\\)/g, '');
        var dirty = qnum.replace('question_', '').replace('_', ':');
        var index = dirty.indexOf(':');

        // We have to get the question
        var the_question = $('#question_' + clean.split('_')[0].replace(/(\.)/g, '')).text().trim();

        //var is_multiple = $('#question_' + clean.split('_')[0].replace(/(\.)/g, '')).parent().parent().hasClass('type_choice-multiple');

        //type_choice-multiple
        console.log('### valchanged:' +value+' ### ')
        console.log(value);
        console.log('### the question:' +value+' ### ')
        
        if ( value===true) {
            console.log('### true')
            //console.log(qnum);
            //console.log(clean.replace('_','. ')+' ('+the_question+')');
            //console.log(value);

            //var optional = $('#question_'+clean.split('_')[0].replace(/(\.)/g,'')).closest('input[type="text"]');
            //console.log(optional.attr('id'));

            //var optional = $('#question_'+just_number.replace(/(\.)/g,'\\.')+"_1_opt").val();

            var pid = bool_container.partialLookup('question_nr_' + dirty.substring(0, index) + "_____");

            var broot = bool_container.getRoot();

            if(broot && pid == broot.id && broot.variables.length > 1){
                bool_container.pushWithDelegate('question_nr_' + dirty.substring(0, index) + "_____" + clean + "_____",
                    clean.replace('_', '. ') + ' (' + the_question + 
                     ')', dirty.substring(index + 1, dirty.length), 'clearcheck("' + $self.attr('id') + '");',
                pid);
            } else {
                bool_container.pushWithDelegate('question_nr_' + dirty.substring(0, index) + "_____" + clean + "_____",
                    clean.replace('_', '. ') + ' (' + the_question +
                     ')', dirty.substring(index + 1, dirty.length), 'clearcheck("' + $self.attr('id') + '");',
                pid, BOOL['OR']);
            }

        } else if ( value === false) {
            console.log('### false')
            var optional = $('#question_' + just_number.replace(/(\.)/g, '') + "_opt").val();
            bool_container.splice('question_nr_' + dirty.substring(0, index) + "_____" + clean + "_____",
                clean.replace('_', '. ') + ' (' + the_question + ')', dirty.substring(index + 1, dirty.length));
        } 
        else {
            console.log('### not true, not false')
            if (value != 'yes' && value != 'no' && value != 'dontknow ')
                bool_container.pushWithDelegate('question_nr_' + clean, clean.replace('_', '') + '. ' + the_question.replace(/\s{2,}/g, ' ') + '',
                    value, 'clear_selection("question_nr_' + clean + '", " ");');
            else{
                    //bool_container.pushWithDelegate('question_nr_' + clean, clean.replace('_', '') +  value,
                    //value, 'clear_selection("question_nr_' + clean + '", " ");');
                    
            }

        }
    }

    qvalues[qnum] = value;
    // qnum may be 'X_Y' for option Y of multiple choice question X
    qnum = qnum.split('_')[0];
    for (var t in qtriggers) {
        t = qtriggers[t];
        checks = getChecksAttr(t);
        var res = eval(checks);
        statusChanged(t, res)
    }

    var context = $(self).closest('[id^="qform"]');
    var dclamp = $('[data-clamp]', context);

    console.log(dclamp.css('display'));

    if(dclamp.css('position') != 'fixed'){
        dclamp.removeAttr('style');
        var off;
        try {
            off = $('.questionset-submit', context).offset().top;
        }catch(err){
            off = 0;
        }
        $('.questionset-submit', context).scrollToFixed( { bottom: -10, limit: off } );
        dclamp.resize();
    }

}

function initialvalchanged(qnum, value, self) {
    qvalues[qnum] = value;
    // qnum may be 'X_Y' for option Y of multiple choice question X
    qnum = qnum.split('_')[0];
    for (var t in qtriggers) {
        t = qtriggers[t];
        checks = getChecksAttr(t);
        var res = eval(checks);
        statusChanged(t, res)
    }
}

function addtrigger(elemid) {
    var elem = document.getElementById(elemid);
    //console.log(elemid + " : " + elem + " : "+document.getElementById(elemid));
    if (!elem) {
        console.error("addtrigger: Element with id " + elemid + " not found.");
        return;
    }
    qtriggers[qtriggers.length] = elem;
}

function clear_selection(question_name, response) {
    var quest = question_name.replace('question_nr_', 'question_');
    var was_checked = $(":radio[name='" + quest + "']").is(':checked');

    $(":radio[name='" + quest + "']").prop('checked', false);
    if (!(typeof bool_container === 'undefined')) {
        bool_container.splice(question_name, response, '');
    }
    if (was_checked) {
        if (!(typeof questionSetsCounters === 'undefined')) {
            var qId = parseInt(quest.split("_")[1]);

            questionSetsCounters[qId]['filledQuestions'] = questionSetsCounters[qId]['filledQuestions'] - 1;

            var ui = new CounterUI();
            ui.updateCountersClean(qId);
        }
    }
}

/*
 - disable the submit button once it's been clicked
 - do it for a total of 5 seconds by which time the page should've been sent
 - oscillate the sending class which does some fancy css transition trickery
*/
function setsaveqs(id, fingerprint_id, q_id, mode) {
    if (!e) var e = window.event;

    $('#' + id).submit(function(e) {
        if (e)
            e.preventDefault();

        var self = $(this);

        if (!(typeof errornavigator === 'undefined')) {
            errornavigator.hideErrorPage();
            $("#loading-message").fadeOut('fast');
            $("#loading-error-message").fadeOut('fast');
            errornavigator.reset();

            if(typeof advValidator !== 'undefined')
                advValidator.reload();

            if(typeof advValidator !== 'undefined')
                var list_invalid = advValidator.validateFormContext(e, self);
            else
                list_invalid = [];

            if (list_invalid.length == 0) {

                if (formHasChanged) {
                    // If its not the first or last
                    var id = this.id.split('_');

                    if (self.length != 0 && id[1] != '0' && id[1] != '99') {

                        // Save this questionset using an ajax post                       
                        var posting = postForm(self);

                        $("#loading-message").fadeIn('fast');

                        posting.done(function(data) {
                            $("#loading-message").fadeOut('fast');
                            $("#success-message").fadeIn('fast').delay(2000).fadeOut('fast');
                            formHasChanged = false;

                            if (data.mandatoryqs && data.mandatoryqs != -1 && data.mandatoryqs != id[1]) {
                                formHasChanged = true;
                                questionsets_handle('qs_' + data.mandatoryqs, fingerprint_id, q_id, mode);

                            }
                        });

                        posting.fail(function(data) {
                            $("#loading-message").fadeOut('fast');

                            $("#loading-error-message").fadeIn('fast');

                        });
                        advValidator.reload();
                    }
                }

                document.body.scrollTop = document.documentElement.scrollTop = 0;

                formHasChanged = false;
                list_invalid = [];

            } else {
                console.log("Jump to errors and show error navigator.");

                for (var i = 0; i < list_invalid.length; i++) {
                    errornavigator.addError('qc_' + list_invalid[i]);
                }
                errornavigator.showErrorPager();

                // jump to first problem
                errornavigator.nextError();

            }

        }

    });
}
QsType = {
    ADD: 0,
    EDIT: 1,
    VIEW: 2,
    SEARCH: 3
}

function postForm(oForm){
    var formData = new FormData(oForm[0]);
    return $.ajax(
        {
            url : oForm.attr("action"),
            type: "POST",
            data : formData,
            processData: false,
            contentType: false,
        });
}

function findQsPath(mode) {
    var commprefix = "";
    var path = ""
    if (mode == QsType.ADD) {
        if(community)
            commprefix = "c/"+community+"/";
        path = commprefix + "addqs/";
    }
    else if (mode == QsType.EDIT)
        path = "editqs/"
    else if (mode == QsType.VIEW)
        path = "detailedqs/"
    else if (mode == QsType.SEARCH) {
        if(community)
            commprefix = "c/"+community+"/";
        path = commprefix + "searchqs/"
    }

    return path;
}

function findPath(mode) {
    var commprefix = "";
    try {
        commprefix = "c/"+community+"/";
    } catch (e) {
        if (e.name !== 'ReferenceError') throw e;
    }   

    var path = ""
    if (mode == QsType.ADD)
        path = "add/";
    else if (mode == QsType.EDIT)
        path = "dbEdit/"
    else if (mode == QsType.VIEW)
        path = "fingerprint/"
    else if (mode == QsType.SEARCH) {
        path = "advancedSearch/"
    }

    return commprefix + path;
}

function loadqspart(fingerprint, pk, sortid, mode) {

    var path = findQsPath(mode);
    var returnable = {};

    if(typeof global_public_key != 'undefined')
        returnable = {
            publickey: global_public_key
        };
    if (sortid != null) {
        console.log($("#qs_" + pk));
        $.get(path + fingerprint + "/" + pk + "/" + sortid + "/", returnable).done(function(data) {
            if (mode == QsType.SEARCH) {
                $("#qs_" + pk).html(data);
            } else {
                $("#qs_" + sortid).html(data);
            }
        });
    } else
        $.get(path + fingerprint + "/" + pk + "/", function(data) {
            $("#qs_" + pk).html(data);
        });

}
var errornavigator;

function initQsEnv(fingerprint_id, q_id, sortid, mode) {
    generateStub();
    $('.reqfield').tooltip({
        container: 'body'
    });
    errornavigator = $('#errornavigator').errornavigator();

    loadqspart(fingerprint_id, q_id, sortid, mode);

    if (mode == QsType.VIEW) {
        if(typeof advValidator !== 'undefined')
            advValidator.searchMode(true);
    }

    initialCounterSetup();

    if (!(window.history && history.pushState)) {
        page = History.getState().hash.split('/')[2];
        if (page)
            questionsets_handle(document.getElementById('qs_' + page).id, fingerprint_id, q_id, mode);
    }

}
// Unused functions (logic was transfered to the backend)
function getPrevSet(){
    var prev_id = $('.nav-pills .active').prev('[id^="li_qs"]').attr('id');
    if(prev_id)
        return prev_id.replace('li_','');
}
function getNextSet(){
    var next_id = $('.nav-pills .active + li').attr('id');
    if(next_id)
        return next_id.replace('li_','');
}
// End of unused functions

var __internal_status = {};

function enforce_empties(id, mode){
    console.log('ENFORCE EMPTIES');

    if(mode !== 'empty' && mode !== 'filled'){
        console.error('Only modes available are empty or filled');
        return false;
    }

    var showing = true;

    if(__internal_status.hasOwnProperty(id+mode)){
        showing = __internal_status[id+mode];
    }

    __internal_status[id+mode] = showing;

    var questionset = $('#qform'+id);

    var answers;

    console.log(showing);

    if(mode === 'empty')
        answers = questionset.find('[id^="answered_"]').filter(":not(:visible)").parent().parent().filter(':not(.dont_hide)').filter(':not(.depon_class)');
    else
        answers = questionset.find('[id^="answered_"]').filter(":visible").parent().parent().filter(':not(.dont_hide)').filter(':not(.depon_class)');

    if(showing){
        var icon = $('#hide_'+mode+'_').find('svg');

        if (icon.length) {
            icon[0].classList.remove("fa-times");
            icon[0].classList.add("fa-check");
        }

        //console.log('Showing empty questions for '+id);
        answers.removeClass('database_listing_away');
    } else {
        var icon = $('#hide_'+mode+'_').find('svg');

        if (icon.length) {
            icon[0].classList.remove("fa-check");
            icon[0].classList.add("fa-times");
        }

        //console.log('Hiding empty questions for '+id);
        answers.addClass('database_listing_away');
    }

    return 'GOT INSIDE';
}

function questionsets_handle(id_questionset, fingerprint_id, q_id, mode) {
    if (!e) var e = window.event;

    var id = id_questionset.split('_');

    active_qset = id[1];
    $('#active_qs').val(id_questionset);
    $('#active_qs_sortid').val(id[1]);

    if(typeof advValidator !== 'undefined')
        advValidator.reload();

    // First we get the previous form
    var previous_id = $('.questionset:not(.hide)').first().attr('id').split('_')[1];
    var current_form = $('#qform' + previous_id);


    if (!(typeof errornavigator === 'undefined')) {
        errornavigator.hideErrorPage();
        $("#loading-message").fadeOut('fast');
        $("#loading-error-message").fadeOut('fast');
        errornavigator.reset();


        var list_invalid;
        if (mode == QsType.VIEW || mode == QsType.SEARCH)
            list_invalid = [];
        else{
            if(typeof advValidator !== 'undefined')
                list_invalid = advValidator.validateFormContext(e, current_form);
            else
                list_invalid = [];
        }

        if (list_invalid.length == 0) {

            if (formHasChanged && (mode != QsType.VIEW) && mode != QsType.SEARCH) {
                // If its not the first or last
                if (current_form.length != 0 && id[1] != '0' && id[1] != '99') {

                    // Save this questionset using an ajax post                       
                    var posting = postForm(current_form);

                    $("#loading-message").fadeIn('fast');

                    posting.done(function(data) {
                        $("#loading-message").fadeOut('fast');
                        $("#success-message").fadeIn('fast').delay(2000).fadeOut('fast');
                        formHasChanged = false;

                        if (data.mandatoryqs && data.mandatoryqs != -1) {

                            formHasChanged = true;
                            questionsets_handle('qs_' + data.mandatoryqs, fingerprint_id, q_id, mode);

                        }
                    });
                    posting.fail(function(data) {
                        $("#loading-message").fadeOut('fast');
                    });
                }
            }
            $('.questionset').each(function(i, obj) {
                    
                    if (obj.id == id_questionset) {
                        $('#' + obj.id).addClass("show");
                        $('#li_' + id_questionset).addClass("active");
                        $('#' + obj.id).removeClass("hide");

                        if ($('#' + obj.id).find('.loadingindicator').length != 0) {
                            if (mode == QsType.SEARCH)
                                loadqspart(fingerprint_id, obj.id.replace("qs_", ""), q_id, mode);
                            else
                                loadqspart(fingerprint_id, q_id, obj.id.replace("qs_", ""), mode);
                            console.log("Loading to dom");
                        } else {
                            console.log("Already on dom");
                            var qstmp = id_questionset.split("_")
                            //loadqspart(fingerprint_id, q_id, obj.id.replace("qs_", ""), mode);
                            $('#qform'+qstmp[1]).resize();
                            
                        }
                        console.log(mode);
                        console.log(findPath(mode));
                        if (mode == QsType.SEARCH){

                            if (window.history && history.pushState) {
                                if(q_id != null){
                                  History.pushState(null, null, findPath(mode) + fingerprint_id + "/" + obj.id.replace("qs_", "")+"/"+q_id);
                                } else {
                                  History.pushState(null, null, findPath(mode) + fingerprint_id + "/" + obj.id.replace("qs_", ""));
                                }
                            }
                        }
                        else{
                            if (mode == QsType.EDIT)
                                History.pushState(null, null, findPath(mode)+ fingerprint_id +"/" + q_id + "/" + obj.id.replace("qs_", ""));
                            else if(mode == QsType.VIEW)
                                History.pushState(null, null, findPath(mode)+ fingerprint_id + "/" + obj.id.replace("qs_", ""));
                            else
                                History.pushState(null, null, findPath(mode) + q_id + "/" + obj.id.replace("qs_", ""));
                        }
                        if(typeof advValidator !== 'undefined')
                            advValidator.reload();
                    } else {

                        $('#li_' + obj.id).removeClass("active");
                        $('#' + obj.id).addClass("hide");
                        $('#' + obj.id).removeClass("show");
                    }

                }

            );
            document.body.scrollTop = document.documentElement.scrollTop = 0;

            list_invalid = [];



        } else {
            console.log("Jump to errors and show error navigator.");

            for (var i = 0; i < list_invalid.length; i++) {
                errornavigator.addError('qc_' + list_invalid[i]);
            }
            errornavigator.showErrorPager();

            // jump to first problem
            errornavigator.nextError();

        }
        console.log('GOT THROUGH HERE');
        enforce_empties(active_qset, 'empty');
        enforce_empties(active_qset, 'filled');
    }
}


function setupHideEmpties(id, mode){
    if(mode !== 'empty' && mode !== 'filled'){
        console.error('Only modes available are empty or filled');
        return false;
    }
    // discover current status, default is inexistent in memory, is showing = true
    var showing = false;

    if(__internal_status.hasOwnProperty(id+mode)){
        showing = !__internal_status[id+mode];
    }

    __internal_status[id+mode] = showing;

    var questionset = $('#qform'+id);

    var answers;

    if(mode === 'empty')
        answers = questionset.find('[id^="answered_"]').filter(":not(:visible)").parent().parent().filter(':not(.dont_hide)').filter(':not(.depon_class)');
    else
        answers = questionset.find('[id^="answered_"]').filter(":visible").parent().parent().filter(':not(.dont_hide)').filter(':not(.depon_class)');

    //console.log(answers);
    if(showing){
        var icon = $('#hide_'+mode+'_').find('svg');

        if (icon.length) {
            icon[0].classList.remove("fa-times");
            icon[0].classList.add("fa-check");
        }

        //console.log('Showing empty questions for '+id);
        answers.removeClass('database_listing_away');
    } else {
        var icon = $('#hide_'+mode+'_').find('svg');

        if (icon.length) {
            icon[0].classList.remove("fa-check");
            icon[0].classList.add("fa-times");
        }

        //console.log('Hiding empty questions for '+id);
        answers.addClass('database_listing_away');
    }
}

function markAnswered(question){
    $('[id="request_'+question+'"]').hide();
    $('[id="answered_'+question+'"]').removeClass('hide');
}
