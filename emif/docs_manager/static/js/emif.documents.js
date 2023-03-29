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


function FingerprintPCAPI()
{

    this.getGenericFilter = function()
    {

        var result = {}

        $.ajax({
          dataType: "json",
          url: "population/genericfilter/Var",
          async: false,
          data: result,
          success: function (data){result=data;},
        });
        return result;

    };
};


function PopulationCharacteristics (type)
{
    this.handle_type_chart = function(e)     {
        e.preventDefault();
        e.stopPropagation();
        console.log("Type of graph is: ");

    };


    this.handle_data = function(data){



    };


};

/** Count number of documents, this could be used to check if the tab is shown
 * or not
 */
function getDocCount(admin){
    var result = {}
    $.ajax({
      dataType: "json",
      type: "POST",
      url: "docsmanager/docfiles/"+getFingerprintID_new()+"/",
      async: false,
      data: { publickey: global_public_key, result:result },
      success: function (data){result=data;},
    });
    var output = 0;

    if(result.conf != undefined && result.conf.length > 0){
        output = result.conf.length;
    }
    return output;
}



function fillList(admin){
        if(isadmin == undefined){
            isadmin=admin;
        }
          $('#files').html('');

          var result = {}

        $.ajax({
          dataType: "json",
          type: "POST",
          url: "docsmanager/docfiles/"+getFingerprintID_new()+"/",
          async: false,
          data: { publickey: global_public_key, result:result },
          success: function (data){result=data;},
        });
        var output = "";

        if(result.conf != undefined && result.conf.length > 0){
            output = '<h4 class="pull-center">Documents Available</h4>';
        } else {
            if(typeof global_owner === 'undefined'){
                output = '<h4 class="pull-center">No documents associated with this database yet.</h4><p class="pull-center">You can upload documents to associate them to the fingerprint browser.</p>';

            } else {
                output = '<h4 class="pull-center">No documents associated with this database yet.</h4><p class="pull-center">This database fingerprint does not have documents yet. Please contact the database owner to get more information.</p>';
            }
        }
        $('#doc_status').html(output);

        result.conf.forEach(function(d){
            //var context = $('<tr>').appendTo('#files');

            var content = "<td><button class=\"btn btn-link\" onclick=\"requestFile('"+
                d.file_name+"','"+d.revision+"')\">" + d.file_name
                            + "</button></td><td>" + d.comments
                            + "</td><td>" + d.latest_date +"</td>";

            if(admin == true)
                content += '<td class="btn_delete" style="width: 50px;"><button class="btn btn-link" '
    + 'onclick="deleteFile(\''+d.file_name+'\',\''+d.revision+'\')">'
    + '<img src="static/img/glyphicons_192_circle_remove.png"/></button></td>';


            var node = $('<tr>').html(content);
            node.appendTo('#files');
            //node.appendTo(context);
        });
}
function requestFile(filename, revision){
    /*$.post( "api/getfile", { filename: filename, revision: revision })
      .done(function(result) {
        console.log(result);
      })
      .fail(function() {
        console.log( "error getting file" );
      });
    */
    var df = $('#downloadfile');
    $('[name="filename"]').val(filename);
    $('[name="revision"]').val(revision);
    $('[name="publickey"]').val(global_public_key);
    $('[name="fingerprint"]').val(global_fingerprint_id);
    df.submit();
}
function deleteFile(filename, revision){
    $.post( "api/deletefile",
        {   fingerprint_id: getFingerprintID_new(),
            filename: filename,
            revision: revision
        })
      .done(function(result) {
        if(result.result){
            alert('Document deleted.');
            fillList(isadmin);

        } else {
            bootbox.alert('It was impossible to delete the document.');
        }
      })
      .fail(function() {
        bootbox.alert( "Error Deleting File" );
      });
}
/********************************************************
**************** Document Manager - Uploads, etc
*********************************************************/


/* JQuery Plugin for Population Characteristics */


 (function( $ )
 {



    var methods = {
        init : function( options ) {
            console.log("init");
            $(".chart_pc" ).on(eventToCatch, options.handle_type_chart);
        },
        draw : function( options ) {


        },

    };

    $.fn.populationCharts = function(method) {
        // Method calling logic
        if ( methods[method] ) {
        return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
        } else if ( typeof method === 'object' || ! method ) {
        return methods.init.apply( this, arguments );
        } else {
        $.error( 'Method ' + method + ' does not exist on jQuery.populationCharts' );
        }
        return this;
    };
}( jQuery ));

$(document).ready(
    function(){

        var pc = new PopulationCharacteristics("pc");

        $("#populationcharacteristics").populationCharts(pc);
        $("#populationcharacteristics").populationCharts('draw', pc);
    }
);

/*jslint unparam: true, regexp: true */
/*global window, $ */
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$(function () {

    'use strict';
    var csrftoken = $.cookie('csrftoken');
    // Change this to the location of your server-side upload handler:
    var url2 = 'docsmanager/uploadfile/'+getFingerprintID_new()+"/",
        uploadButton = $('<button/>')
            .addClass('btn btn-primary')
            .prop('disabled', true)
            .text('Processing...')
            .on('click', function () {
                var $this = $(this),
                    data = $this.data();
                $this
                    .off('click')
                    .text('Abort')
                    .on('click', function () {
                        $this.remove();
                        data.abort();
                    });
                data.submit().always(function () {
                    $this.remove();
                });
            });
    $('#fileupload').fileupload({
        url: url2,
        crossDomain: true,
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        dataType: 'json',
        autoUpload: false,
        acceptFileTypes: /(\.|\/)(gif|jpe?g|png|pdf|xlsx?|docx?|tsv|txt|zip)$/i,
        maxFileSize: 20000000, // 20 MB
        // Enable image resizing, except for Android and Opera,
        // which actually support image resizing, but fail to
        // send Blob objects via XHR requests:
        disableImageResize: /Android(?!.*Chrome)|Opera/
            .test(window.navigator.userAgent),
        previewMaxWidth: 100,
        previewMaxHeight: 100,
        previewCrop: true
    }).on('fileuploadadd', function (e, data) {
        console.log('File Upload - fileuploadadd');
        data.context = $('<tr>').appendTo('#files');
        $.each(data.files, function (index, file) {
            var node = $('<td>').text(file.name);

            node.appendTo(data.context);

            var node2 = $('<td class="fmessage">');

            node2.appendTo(data.context);

            if (!index) {
                uploadButton.clone(true).data(data).appendTo(data.context).wrap('<td style="text-align: right; width: 100px;">');
            }

        });
    }).on('fileuploadprocessalways', function (e, data) {
        console.log('File Upload - fileuploadprocessalways');
        var index = data.index,
            file = data.files[index],
            node = $(data.context.find('.fmessage'));
        if (file.preview) {
            node
                .prepend(file.preview);
        }
        if (file.error) {
            node.text(file.error);
        }
        if (index + 1 === data.files.length) {
            data.context.find('button')
                .text('Upload')
                .prop('disabled', !!data.files.error);
        }
    }).on('fileuploadprogressall', function (e, data) {
        var progress = parseInt(data.loaded / data.total * 100, 10);

        bootbox.dialog({
            message: "<h3>Uploading, please wait.</h3>"
        });

        $('#progress .progress-bar').css(
            'width',
            progress + '%'
        );
    }).on('fileuploaddone', function (e, data) {
        bootbox.hideAll();
        $.each(data.result.files, function (index, file) {
            var link = $('<a>')
                .attr('target', '_blank')
                .prop('href', file.url);
            var td = $(data.context.children()[index]);
            td.wrapInner(link);
        });

        fillList(isadmin);

    }).on('fileuploadfail', function (e, data) {
        bootbox.hideAll();
        $.each(data.result.files, function (index, file) {
            var error = $('<span/>').text(file.error);
            $(data.context.children()[index])
                .append('<br>')
                .append(error);
        });
    }).prop('disabled', !$.support.fileInput)
        .parent().addClass($.support.fileInput ? undefined : 'disabled');
});
