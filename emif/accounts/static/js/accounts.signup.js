/*# -*- coding: utf-8 -*-
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
#*/


var termsAvailable = false;
var captchaDone = false; 


function makeSubmitUnvailable(){
    $("#createaccount").addClass('btn-gray');
    $("#createaccount").removeClass('btn-primary');
    document.getElementById("createaccount").disabled = true;
};

function makeSubmitAvailable(){
    if (termsAvailable && captchaDone){
        $("#createaccount").removeClass('btn-gray');
        $("#createaccount").addClass('btn-primary');
        document.getElementById("createaccount").disabled = false;
    }
    
}


function checkAccept() {
    
    if (document.getElementById("Iaccept").checked == true) {
        termsAvailable = true; 
        makeSubmitAvailable();

    }
    else {
        termsAvailable = false; 
        makeSubmitUnvailable();
    }
}

var focusFirstField = function () {
    $('#signup_form input:nth(1)').focus();
};
//$('#signup_form input[type="text"], #signup_form input[type="password"], #signup_form select').addClass('col-md-4');
$('#signup_form button[type="reset"]').on('click', focusFirstField);
focusFirstField();
/* I swear, i can't seem to be able to edit the damn forms from django_userena other way
* It's like they think people don't want to change the layout easily...
*/
$('#signup_form .control-label').each(function (e) {
    var fore = '#' + $(this).attr('for');
    var destiny = $(fore);

    if (destiny.get(0)) {
        var content = $(this).text().trim();

        $(destiny).prop('placeholder', content);

        $(this).hide();
    }
});
$('label[for="id_paginator"]').show();


var feedbackRecaptchaCallback = function(){
    captchaDone = true;
    makeSubmitAvailable();
};