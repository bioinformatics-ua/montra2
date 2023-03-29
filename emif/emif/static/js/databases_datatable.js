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
#
*/
/******* All Databases data table specific Javascript ****/
// Global variable that nows if the checkboxes are all selected or not
selected_checkboxes = false;

$(document).ready(function() {
    $('#tabular_container').html('<div class="panel panel-default pull-center"><div class="panel-body">To see a tabular view of selected databases, please choose the questions and the databases and select "Export".</div></div>');
    $('#db_type').selectpicker();
    // Add handlers to the db type selector
    $('#db_type').change(function() {
        var value_selected = $(this).val();
        if (value_selected == '0') {
            $('.qsets').each(function() {
                $(this).addClass('depon_class');
                $('#submit_dbs_qsets').addClass('depon_class');
            });
        } else {
            $('.qsets').each(function() {
                if ($(this).attr('id') == 'q_select_' + value_selected.replace(/\s+/g, '')) {
                    $(this).removeClass('depon_class');
                    //$(this).val('0');
                    $('#submit_dbs_qsets').removeClass('depon_class');
                } else
                    $(this).addClass('depon_class');
            });
        }
    });
    $('#submit_dbs_qsets').click(function() {

       


        //get selected databases
        var selected_databases =[];
        $("input[name='chkname']:checked").each(function (i) {
            console.log($(this).val());
             if($(this).val() != 'all'){
                selected_databases[i] = $(this).val();
             }
            });

        // get db type
        var db_selected = $('#db_type').val();

        // get qsets
        var qsets_selected = [];
        var qsets_selected_dict = {};

        var qsets_checkbox_selected = [];
        var parent_name_array = [];
        var parent_name = [];

        qsets_checkbox_selected = $('.jstree').jstree('get_selected'); 

        for (i=0; i< qsets_checkbox_selected.length; i++)
        {
            parent_name_array = $('.jstree').jstree().get_path(qsets_checkbox_selected[i], '', true);
            parent_name = parent_name_array[0];
            qsets_selected.push(qsets_checkbox_selected[i].split("_")[1]);
            qsets_selected_dict[parent_name] = qsets_selected;

        }
    

        if (qsets_selected.length == 0) {
            bootbox.alert("There is no question selected. Please select at least one to see the datatable view.");
            $('#tabular_container').html('<div class="well pull-center">To see a tabular view of all databases, please choose the questions and databases and select "Show Datatable".</div>');
        }
         else if (selected_databases.length == 0) {
            bootbox.alert("There is no database selected. Please select at least one to see the datatable view.");
            $('#tabular_container').html('<div class="well pull-center">To see a tabular view of all databases, please choose choose the questions and databases and select "Show Datatable".</div>'); 
        
         }
        else {
            $('#tabular_container').html('<div class="well pull-center">Loading...</div>');

           
            //$('#qsets_div').hide();
            //$('#dbs_div').hide();

            //$("#submit_dbs_qsets").prop("disabled", true);
            $("#exportdatatable").prop("disabled", false);

            $.post("qs_data_table", {
                db_type: db_selected,
                qsets: qsets_selected,
                questions_dict: JSON.stringify(qsets_selected_dict),
                selected_databases: selected_databases,
            })
                .done(function(data) {
                    $('#tabular_container').html(data);
                });
        }

    });

    $('#exportdatatable').click(function() {
        //get selected databases
        var selected_databases =[];
        $("input[name='chkname']:checked").each(function (i) {
            if($(this).val() != "all"){
                selected_databases[i] = $(this).val();
            }
            });

        // get db type
        var db_selected = $('#db_type').val();

        // get qsets
        var qsets_selected = [];
        var qsets_selected_dict = {};

        var qsets_checkbox_selected = [];
        var parent_name_array = [];
        var parent_name = [];

        qsets_checkbox_selected = $('.jstree').jstree('get_selected'); 

        for (i=0; i< qsets_checkbox_selected.length; i++)
        {
            parent_name_array = $('.jstree').jstree().get_path(qsets_checkbox_selected[i], '', true);
            parent_name = parent_name_array[0];
            qsets_selected.push(qsets_checkbox_selected[i].split("_")[1]);
            qsets_selected_dict[parent_name] = qsets_selected;

        }  
             $.post("export_datatable", {
                 db_type: db_selected,
                 qsets: qsets_selected,
                 questions_dict: JSON.stringify(qsets_selected_dict),
                 selected_databases: selected_databases,
             })
                 .done(function(data) {
                //window.location = ("/export_message");
                window.location.replace("./export_message");
                 });
       
    });

});

function selectall(){

    var checkboxes = document.getElementsByName('chkname');
    var selected_checkboxes = $('.jstree').jstree('get_selected'); 
    var all_checkboxes = jQuery.jstree.reference('.jstree').get_json('#', { flat: true });
   
    if(selected_checkboxes.length == all_checkboxes.length){
        all_checkboxes_selected = true;
    }
    else{
        all_checkboxes_selected = false;
    }

    if(all_checkboxes_selected){
        $(".jstree li[role=treeitem]").each(function () {
        $(".jstree").jstree('deselect_node', this)
});

        for (var i = 0; i < checkboxes.length; i++) {
             if (checkboxes[i].type == 'checkbox') {
                 checkboxes[i].checked = false;
             }
         }

        all_checkboxes_selected = false;

    }
    else{
   $(".jstree li[role=treeitem]").each(function () {
     $(".jstree").jstree('select_node', this)
});

     for (var i = 0; i < checkboxes.length; i++) {
             if (checkboxes[i].type == 'checkbox') {
                 checkboxes[i].checked = true;
             }
         }

    all_checkboxes_selected = true;
    }
}


function selectall_databases(elem){

    var checkboxes = document.getElementsByName('chkname');


    if (elem.checked) {
         for (var i = 0; i < checkboxes.length; i++) {
             if (checkboxes[i].type == 'checkbox') {
                 checkboxes[i].checked = true;
             }
         }
     } else {
         for (var i = 0; i < checkboxes.length; i++) {
             if (checkboxes[i].type == 'checkbox') {
                 checkboxes[i].checked = false;
             }
         }
     }
 }


 function selectall_questionsets(elem){

    var selected_checkboxes = $('.jstree').jstree('get_selected'); 
    var all_checkboxes = jQuery.jstree.reference('.jstree').get_json('#', { flat: true });
   
    
    if(elem.checked){
        $(".jstree li[role=treeitem]").each(function () {
            if(! $(".jstree").jstree().is_disabled(this) )
                $(".jstree").jstree('select_node', this)
});

    }
    else{
   $(".jstree li[role=treeitem]").each(function () {
        if(! $(".jstree").jstree().is_disabled(this) )
            $(".jstree").jstree('deselect_node', this)
});
    }
}

function check_checked(elem){

    var checkboxes = document.getElementsByName('chkname');
    var all = document.getElementById("chkname_all");
    var count = 0;

        for (var i = 0; i < checkboxes.length; i++) {
             if (checkboxes[i].checked) {
                 count ++;
             }
         }
     
        if (count == checkboxes.length){
            all.checked = true;
        }

        else {
            all.checked = false;
        }

}

function check_checked_tree(elem){

    var selected_checkboxes = $('.jstree').jstree('get_selected'); 
    var all_checkboxes = jQuery.jstree.reference('.jstree').get_json('#', { flat: true });
    var all = document.getElementById("chkname_qset");

    if (selected_checkboxes.length >= 1 ){

        $("#submit_dbs_qsets").prop("disabled", false);
    }

    else{
        $("#submit_dbs_qsets").prop("disabled", true);
    }
}
