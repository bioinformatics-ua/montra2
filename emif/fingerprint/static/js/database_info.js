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
 var bool_container;
 var expanded = false;

 function collapse_expand(context, target) {
     if ($(context).text().indexOf('Collapse') !== -1) {
         expanded = false;
         $(context).html('<i class="icon-plus"></i>&nbsp; Expand');
         //change_name_collapse(false);
         console.log();
         $(target+" .panel-collapse").collapse("hide");


     } else {
         expanded = true;
         $(context).html('<i class="icon-minus"></i>&nbsp; Collapse');
         //change_name_collapse(true);
         $(target+" .panel-collapse").collapse("show");

         if(target == '#setsumm_container')
            loadRemainingQsets();
     }
 }

 $.fn.textWidth = function() {
     var node, original, width;
     original = $(this).html();
     node = $("<span style='position:absolute;width:auto;left:-9999px'>" + original + "</span>");
     //node.css('font-family', $(this).css('font-family')).css('font-size', $(this).//css('font-size'));
     $('body').append(node);
     width = node.width();
     node.remove();
     return width;
 };
 /* TODO: Toggle + Expand all
             $('.').on('click', function(e) {
             e.preventDefault();
             var $this = $(this);
             var $collapse = $this.closest('.collapse-group').find('.collapse');
             $collapse.collapse('toggle');
             });
             */

 function addTooltip(table_id) {
     if (isSafari()) {
         $('td', $(table_id)).each(function() {
             $(this).removeAttr("title");
         });
     } else {

         /* I decided to change this as this is was a very intensive process,
            I instead tagged them, and add to the class the instance, this way i only have on instance per, table
            declaring a tooltip instance every td...*/
        console.log($(table_id+' > tbody > tr > td.tooltipped'));
         $(table_id+' > tbody > tr > td.tooltipped').each(function() {
             var content = $(this).text().replace(/\s+/gi, ' ');
             if ($(this).textWidth() < $(this).width()) {
                 $(this).removeClass('tooltipped');
             }
         });

         $('.tooltipped', $(table_id)).tooltip({
             container: "body",
             html: true
         });

     }
 }

 function isSafari() {
     if (navigator.userAgent.indexOf('Safari') != -1 && navigator.userAgent.indexOf('Chrome') == -1) {
         return true;
     }
     return false;
 }

 function initializeQset(sortid) {
     addTooltip('#t2_' + sortid);
     $('.captioned_content .summary_content', $('#t2_' + sortid)).expander({
         slicePoint: 68,
         expandText: 'more',
         userCollapseText: 'less'
     });

     $('.comment_button', '#t2_' + sortid).popover({
         trigger: 'hover',
         html: true,
         template: '<div class="popover popover-medium"><div class="arrow"></div><div class="popover-inner"><h3 class="popover-title"></h3><div class="popover-content"><p></p></div></div></div>'
     });

    $(function(){
        $('.requestanswerbtn', $('#t2_'+sortid)).click(function(e){
            var answer = $(this).data("question");

            askForAnswer(answer);

        });
        $('.value_content').mouseover(function(e){
            $(this).find('.requestlabel').show();
        });
        $('.value_content').mouseout(function(e){
            $(this).find('.requestlabel').hide();
        });
    });

 }
 var abortAllRequests = function() {
     for (var request in ajaxRequests) {
         if (ajaxRequests.hasOwnProperty(request)) {
             ajaxRequests[request].abort();
         }
     }
     ajaxRequests = {};
 }
 var threadpool = new TaskQueuer(20, 200);
 var threads = {};
 var thread_priority = 1;
 var ajaxRequestId = 10000;
 var ajaxRequests = {};

 /**
   * This enforces empty rows removal (because of lazy loading and such, we must reapply this after each load to maintain consistency)
   */
 function enforceEmpties() {
     var self = $('#show_hide_button');

     if (self.hasClass('hiding_empty')) {
         hideEmpties(self);
     } else {
         showEmpties(self);
     }
 }

 function showEmpties(self) {
     self.removeClass('hiding_empty');
     self.text('Hide Empty');

     // Show empty
     $('.hide_empty_content').removeClass('hide_empty_content');

     // double check expansions
     //$("#collapseall_metadata").click();
     //$("#collapseall_metadata").click();
 }

 function hideEmpties(self) {
     self.addClass('hiding_empty');
     self.text('Show Empty');

     $('.empty').parent().parent().parent().each(function() {
         var visible = $(this).is(":visible");
         if (visible === true) {
             $(this).addClass('hide_empty_content');
         }
     });
 }

 function initDatabaseInfo(json_aux) {
     load_questionnary();

     /**
      * On tab change, to literature tab, lazy load literature tab
      */
     $(document).on('shown', 'a[data-toggle="tab"]', function(e) {
         /*if ($(e.target).text().toLowerCase().indexOf('literature') != -1) {
             // if not loaded yet
             if ($('#literature').find('.loadingsection').length != 0) {
                 console.log("Loading literature, since it was not loaded yet.");

                 if (global_is_authenticated === true) {
                     $.get("literature/" + global_fingerprint_id,
                         function(data) {
                             $("#literature").html(data);
                         }
                     );
                 } else {
                     $.post("literature/" + global_fingerprint_id, {
                             publickey: global_public_key
                         },
                         function(data) {
                             $("#literature").html(data);
                         }
                     );
                 }

             }

         }*/
     });
     /**
      *  Setup show hide button event
      */
     $('#show_hide_button').click(function() {
         var self = $(this);
         if (self.hasClass('hiding_empty')) {
             showEmpties(self);
         } else {
             hideEmpties(self);
         }
     });

     $('#li_workspace').addClass("active");


     $("#collapseall_metadata").bind('click', function(e) {
         //e.preventDefault();
         //e.stopPropagation();
         collapse_expand(this, '#setsumm_container');

         return false;
     });

     $("#collapseall_summ").bind('click', function(e) {
         //e.preventDefault();
         //e.stopPropagation();
         collapse_expand(this, '#set_container');
         return false;
     });

     $('.popover').popover({
         container: 'body'
     });

     $(".tooltipit").tooltip({
         container: "body"
     });

     // On expand event, we burst the priority of this thread to load before the others
     $('.panel-heading').click(function() {
         var content = $('.panel-body', $(this).parent());
         if (!content.parent().hasClass('in') && content.find('.loadingsection').length != 0) {

             var sortid = -1;
             try {
                 sortid = $('.panel-body', $(this).parent()).attr('id').split('_')[2];
             } catch (err) {
                 console.error("Error retrieving sortid for qs lazy loading");
             }
             console.log('Loading qs ' + sortid);

             abortAllRequests();
             threadpool.abort();

             loadqspartsumm(sortid, global_fingerprint_id);

             if (expanded) {
                 loadRemainingQsets();
             }


         }
     });
     $('.tabbable a[data-toggle="tab"]').on('shown.bs.tab', function(e) {
         if (e.target.textContent.trim() == 'Population Characteristics') {
            console.log('CRITICAL HIT');
             $('.graphTypes').first().click();
         }
     });
     //$('#summarynav').affix();
    /*var sm = $('#summarynav');
    setInterval(function() {
        var offset = $(window).scrollTop();

        if(offset > 0){
            sm.addClass('summarynav_affixed');
        } else {
            sm.removeClass('summarynav_affixed');
        }
    }, 250);
*/
 }

 function initAdvSearchPlugin(serialization_query, query_type, query_id) {

     bool_container = $('#bool_container').boolrelwidget({
         view_only: true,
         view_serialized_string: serialization_query,
         link_back: MontraAPI.getBaseCommunity() + "advancedSearch/" + query_type + "/1/" + query_id
     });
 }

 function loadqspartsumm(sortid, pk) {
    var commprefix = "";
    if(community)
        commprefix = "c/"+community+"/";

     if (global_is_authenticated === true) {
         var request = $.ajax({
             url: commprefix + "fingerprintqs/" + pk + "/" + sortid + "/",
             type: 'GET',
             success: function(data) {
                 delete ajaxRequests[ajaxRequestId];
                 $("#qs_summ_" + sortid).html(data);

                 enforceEmpties();
             },
         });
         ajaxRequests[ajaxRequestId++] = request;

     } else {
         var request = $.ajax({
             url: commprefix + "fingerprintqs/" + pk + "/" + sortid + "/",
             type: 'POST',
             data: {
                 publickey: global_public_key
             },
             success: function(data) {
                 delete ajaxRequests[ajaxRequestId];
                 $("#qs_summ_" + sortid).html(data);

                 enforceEmpties();
             },
         });

         ajaxRequests[ajaxRequestId++] = request;
         threads[sortid] = true;
         try {
             this.complete();
         } catch (err) {}
     }
 }
 /**
  * Since we allow expand all functionalities, we must still load all questionsets when they are all open at once
  * and this is done as was done before, with threadpool (lazy loading one qset doesnt need threadpool)
  */
 function loadRemainingQsets() {
     threadpool = new TaskQueuer(20, 200);
     var not_loaded = findRemainingQsets();
     for (var i = 0; i < not_loaded.length; i++) {
         var thread = new Runnable(loadqspartsumm, thread_priority++, not_loaded[i], global_fingerprint_id);
         threadpool.run(thread);
         threads[not_loaded[i]] = thread;
     }
 }

 function findRemainingQsets() {
     var not_loaded = []
     $('[id^="qs_summ_"]').each(function(key, value) {
         if ($(value).find('.loadingsection').length != 0)
             not_loaded.push(value.id.split("_")[2]);
     });

     return not_loaded;
 }
var tm;
var loaded_arr = [];
var arr_len;


/* this may seem dumb, but we can only run the dashboard after all plugins finished loading
event remote one's with external dependencies that could potentially take a bit.
*/
var tabFull = function(insert){
    loaded_arr.push(insert);

    if(arr_len == loaded_arr.length)
        loadTab();
}
$(function(){
    tm = $('#tab-plug').tabmanager(
        {
            showRegistry: false,
            //registryTarget: "#tabselectbox",
            initial: function () {
                /*tm.addWidget("extrainfo");
                tm.(addWidget)("literature");
                tm.addWidget("discussion");
                */
            }
        }
    );

    $('#summ_btn').click(function(){
    var detview = $('#det_view');
    var sumview = $('#sum_view');
    var sumbtns = $('#summ_btns');
    var detbtns = $('#det_btns');

        if(detview.is(":visible")){
            console.log('SHOW SUMM');
            detview.hide();
            sumview.show();
            sumbtns.show();
            detbtns.hide();
            $(this).html('<i class="fas fa-fw fa-info"></i> &nbsp; Detailed');
        } else {
            console.log('SHOW DETAIL');
            detview.show();
            sumview.hide();
            sumbtns.hide();
            detbtns.show();

            $(this).html('<i class="fas fa-fw fa-list"></i> &nbsp; Summary');
        }

    });

});

function sandbox(id, data, pos){
    var confs, plugin;
    var self;

    try {
        if(typeof data === 'string'){
            eval(data);
            self = {confs: confs, plugin: plugin, has_content:has_content};
        }
        else{
            data(function(confs, plugin, has_content){
                self = {confs: confs, plugin: plugin, has_content:has_content};
            })
        }
    
        if(checkIntegrity(self)){
            self.confs.id = id;
            self.confs.pos = pos;
            registerShell(self);
        }
    } catch(exc){
        console.error("The code contains one or several errors, and doesn't execute, please double check your code. Errors are available on console.");
        console.error(exc);
    }
};

function registerShell(closure){
    console.log('register');
    tm.register(
        new PlugShellWidget(
            closure.confs, closure.plugin
        )
    );

    tabFull(closure.confs.id);
}

function checkIntegrity(closure){
    if(!closure.confs || !(typeof closure.confs == 'object'))
        throw 'You must specify a \'confs\' dictionary for the plugin.';

    if(!closure.plugin || !(typeof closure.plugin == 'function'))
        throw 'You must specify a \'plugin\' function for the plugin.';

    return true;
}

function loadTab(){
    console.log('load tab manager');
    /*var any_configuration = tm.loadConfiguration();

    if(any_configuration == false){*/
        tm.initial();
    /*}*/

    $('#tabreset').tooltip({
        'container': 'body'
    });
}
