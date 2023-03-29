/**********************************************************************
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
***********************************************************************/

var eventToCatch = 'click';
// This is just for interface propuses, the validation is done serverside but we dont
// obviously want to show the button anyway
var isadmin;

/* Population Characteristics */

function divDisplayFolderDeletion(folder_name, community_slug)
{
   if (confirm("Are you sure you want to delete this folder and all its documents?") == true) {   

    $.post( "api/deletecommunityfolder",
        {
            folder_name: folder_name,
            community_slug: community_slug,
        })
      .done(function(result) {
        if(result.result){
            alert('Folder deleted.');
            window.location.href = "/docsmanager/list_community_folders/" + community_slug + "/";

        } else {
            bootbox.alert('It was impossible to delete the folder.');
        }
      })
      .fail(function() {
        bootbox.alert( "Error Deleting Folder." );
      });
 }
}


function divDisplayFunction(file_id, file_name, file_description, name, required) {
  
    var elm_file_description  = document.getElementById("cd_comments");
    elm_file_description.value = file_description;

    var elm_file_id  = document.getElementById("cd_id");
    elm_file_id.value = file_id;

    $( "#uploaddiv" ).dialog();
    $( "#uploaddiv" ).dialog("option", "width", $(window).width()*0.6);
    $( "#uploaddiv" ).dialog("option", "title", "Documentation Upload");

    var elm_choose_file = document.getElementById("choose_file");
    elm_choose_file.required = required;

    
    if(file_id){
        var elm_add_files  = document.getElementById("add_files");
        elm_add_files.value="Save changes"
    }

    var elm_upload_file_name  = document.getElementById("upload_file_name");
    elm_upload_file_name.innerHTML = "<i class='fas fa-fw fa-paperclip'></i>" + name;
    elm_upload_file_name.style.display="block";

    $('#uploaddiv').on('dialogclose', function(event) {
    elm_file_description.value = "";
    elm_upload_file_name.innerHTML = "";
    
 });
}

function divDisplayFolderCreation(){

        $( "#newfolder" ).dialog();
        $( "#newfolder" ).dialog("option", "title", "Create new folder");

        $('#uploaddiv').on('dialogclose', function(event) {
        $('#folder_name_input').value = "";
        $('#folder_description').value = "";
        $('#folder_id').value = "";
    
 });

      

}

function divDisplayFolderEdition(folder_name, folder_description, folder_id,community_slug){

    var elm_folder_name  = document.getElementById("folder_name_input");
    elm_folder_name.value = folder_name;

    var elm_folder_description  = document.getElementById("folder_description");
    elm_folder_description.value = folder_description;

    var elm_folder_id  = document.getElementById("folder_id");
    elm_folder_id.value = folder_id;

    $( "#newfolder" ).dialog();
    $( "#newfolder" ).dialog("option", "title", "Edit folder");

    $('#newfolder').on('dialogclose', function(event) {
   
    elm_folder_name.value = "";
    elm_folder_description.value = "";
    elm_folder_id.value = "";
    
 });


    }

function requestFile(filename, revision){

    var df = $('#downloadfile');
    $('[name="filename"]').val(filename);
    $('[name="revision"]').val(revision);
    df.submit();


}



function deleteCommunityFile(filename, revision, community_slug,show_alert){

 if (confirm("Are you sure you want to delete this document?") == true) {   

    $.post( "api/deletecommunityfile",
        {
            filename: filename,
            revision: revision,
            community_slug:community_slug,
        })
      .done(function(result) {
        if(result.result){
            if(show_alert){
            alert('Document deleted.');}
             window.location.href = "/docsmanager/list_community_folders/" + community_slug + "/";


        } else {
            bootbox.alert('It was impossible to delete the document.');
        }
      })
      .fail(function() {
        bootbox.alert( "Error Deleting File" );
      });
 }
}

function quitBox(cmd)
{   
    if (cmd=='quit')
    {
        open(location, '_self').close();
    }   
    return false;   
}

function closePopup(popup_name)
{

var elm_popup_name  = document.getElementById(popup_name);
$(elm_popup_name).dialog('close');

return false

}

function drag(event) {
    event.dataTransfer.setData("text", event.target.id);

}


function allowDrop(event) {
    event.preventDefault();
}

function drop(event, community_slug) {
    event.preventDefault();

    var source_id = event.dataTransfer.getData("text");
    var row_id = "row_" + source_id;
    var destination_id = event.target.id


    if( document.getElementById(row_id) !== null)
    {


    if(destination_id === source_id)
    {
         return false;
    }

    else

    {
        document.getElementById(row_id).style.display="none";

        $.ajax({
          dataType: "json",
          type: "POST",
          url: "docsmanager/drag_community_folder/" + community_slug + '/' + source_id +  "/" + destination_id + "/" ,
          async: false
        });
}

    }


    else{

    var row_file_id = "rowfile_" + source_id;

     document.getElementById(row_file_id).style.display="none";

        $.ajax({
          dataType: "json",
          type: "POST",
          url: "docsmanager/drag_community_file/" + community_slug + '/' + source_id +  "/" + destination_id + "/" ,
          async: false
        });
}



    }


