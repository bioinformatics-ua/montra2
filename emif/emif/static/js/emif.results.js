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
var counter = 0;
var a;
var bool_container;

function initializePaginatorSorter(base_filter, selected_name, selected_value, extra, allFields){
    a = new PaginatorSorter("table_databases", base_filter, selected_name, selected_value, extra, allFields);

    //TO Be Applied in future releases.
    a.atachPlugin(new SelectPaginatorPlugin());

  if(a != undefined && a.plugin != undefined){

    const dbcount = updateSelectCount();

    counter = dbcount;

    if(dbcount >= 2){
      $("#comparabtn").removeAttr('disabled');
        $("#comparabtn").bind('click',function(e)
        {
          $('#compare_form').attr('action', 'resultscomp');
          postComparison(true);
          return false;
        });

    }

  }

    $('a[href="#"]').attr('href', function(i, val){
        return window.location + val;
    });

    $('.help_selectresults').tooltip({container: 'body', 'html': true});
    $('.tooltippable').tooltip({container: 'body', 'html': true});


}
function setRefineEvent(is_advanced, query_type, query_id){
      $("#refine_search_btn").click( function(){
      if(is_advanced)
        window.location.replace(MontraAPI.getBaseCommunity()+"advancedSearch/"+query_type+"/1/"+query_id);
      else
        $("input[name=query]").focus();

    });
}

function setBooleanPlugin(serialization_query, query_type, query_id){
    bool_container = $('#bool_container').boolrelwidget(
        {
          view_only: true,
          view_serialized_string: serialization_query,
          link_back: MontraAPI.getBaseCommunity()+"advancedSearch/"+query_type+"/1/"+query_id,
          extra_buttons: '\
          <button style="margin-right: 5px; margin-top: 5px; margin-bottom: 5px;" class="pull-right btn btn-success" data-toggle="modal" data-target="#saveQuery"><i class="fas fa-fw fa-save"></i> &nbsp;Save Query</button>\
          '
        }
    );

    window.setTimeout(function(){window.location.hash = "#back";}, 100);
    window.setTimeout(function(){window.location.hash = "#search";}, 100);

      /* This is a trick, to be able to redirect on back button since browsers try to prevent us to do so
       I must do this, because the back url is different from the url on history */
    window.onhashchange = function(){
       if (location.hash == "#back") {
            // comment this because it was making the browser redirect several times after a search
            //window.location.replace($('#base_link').prop('href')+"advancedSearch/"+query_type+"/1/"+query_id);
        }

    }
}

function updateSelectCount(){

    try{
    var dbs = a.plugin.getExtraObjects().selectedList;
    var type = a.plugin.typedb;

    if(type)
      $('#selected_dbstype').text(type);
    else
      $('#selected_dbstype').text("---");

    $('#selected_dbscount').text(dbs.length);

    return dbs.length;

    } catch(err){
      $('#selected_dbscount').text(0);
    }

    return 0;
}

function updateSelectCountJs(type, count) {
  if (type) {
      $('#selected_dbstype').text(type);
  }

  if (count) {
      $('#selected_dbscount').text(count);
      $('#selectFingerprintsLiId').removeClass('disabled')
      $('#selectFingerprintsMultimontraLiId').removeClass('disabled')
  }

  //disabled extract selected fingerprints if none is selected
  if (!count || count === 0) {
      $('#selectFingerprintsLiId').removeClass('disabled').addClass('disabled');
      $('#selectFingerprintsMultimontraLiId').removeClass('disabled').addClass('disabled');
  }
}

function hidecheckbox()
{
  $('.chkbox').toggle();
}

$("#comparabtn").bind('click',function(e)
        {

          e.preventDefault();
          e.stopPropagation();

          if(counter < 2){
            bootbox.alert('Please select at least two databases, using the checkbox on the right side of the table.');
          }
          return false;
        });

//$("#comparabtn").unbind();
function postComparison(isdbs){
  //$('#result_form').submit();
  //console.log('A: '+a);
  //console.log('A-plugin: '+a.plugin);
  if(a != undefined && a.plugin != undefined){
    $('#comparedbs').html('');

    var dbs = a.plugin.getExtraObjects().selectedList;
    //console.error(dbs.length);
    for(var i=0;i<dbs.length;i++){
      $('#comparedbs').append('<input type="checkbox" name="chks_'+dbs[i]+'" checked>');
    }
    var ids = [];
    $('[name^="chks_"]').each(function(){

      var id = $(this).attr('name').split('_')[1];

      ids.push(id);

    });
    if(!isdbs)
      checkExistsPopulation(ids);
    else $('#submitdbsimulate').click();
  }

}

$('.chkbox').click(function()
{
  onDatabaseEntryCheckboxClick(this)
});

function onDatabaseEntryCheckboxClick(e){
  if($(e).is(':checked')){
      counter++;
  } else
  {
      counter--;
  }


  var community = $('#communityindicator').val();

  if(counter == 0){
    updateSelectCountJs("---", ""+counter);
    $('input.chkbox').prop("disabled", false);

    //$("#comparabtn").attr("disabled", true);

  }
  else if(counter == 1){
    
    //$("#comparabtn").attr('disabled', true);

    var checkedtype;
    if(a != undefined && a.plugin != undefined && a.plugin.typedb !=undefined){
      checkedtype = a.plugin.typedb;
    } else {
      checkedtype = $('.chkbox:checked').first().attr('typedb');
    }
    updateSelectCountJs(checkedtype, counter);

    $('input.chkbox').prop("disabled", false);

    $('input.chkbox:not([typedb="' + checkedtype
    + '"])').prop('disabled', true);


  }
  else if (counter >= 2){
    updateSelectCountJs(null, counter);
    //$("#comparabtn").attr('disabled', false);
      $("#comparabtn").bind('click',function(e)
      {
        if(community.length > 0)
          $('#compare_form').attr('action', 'c/'+community+'/resultscomp');
        else
          $('#compare_form').attr('action', 'resultscomp');
        postComparison(true);
        return false;
      });
  }
}

$('[rel=tooltip]').tooltip({container: 'body', 'html': true});

$('.popover').popover({
    container: 'body'
});
$('.accordion-body.collapse').hover(
function () {
$(this).css('overflow','visible');
},
function () {
  $(this).css('overflow','hidden');
}
);

$(function(){
  $('#query_title_save').click(function(){
    var title = $('#query_title').val();
    var id = $('#query_id').val();

    if(title && title.trim().length > 0){
      $.post('advsearch/savename', {
          title: title,
          id: id
      })
      .done(function(result) {
        $('#saveQuery').modal('hide');
      })
      .fail(function() {
        bootbox.alert('Could not save the advanced query. If the problem persists, please contact the administrator.')
      });
    }

  });

  var tsi = $('#type_search_icon');
  var ts = $('#type_search');

    if(supports_html5_storage()){
        var collapsed = localStorage.getItem("montra-search-collapsed");

        if(collapsed == 'false'){
         tsi.data('status', 1);
          tsi.html('<i class="fas fa-fw fa-minus"></i>');
          ts.show();
        }
    }

  tsi.click(function(){
    if($(this).data('status') == 0){
      $(this).data('status', 1);
      tsi.html('<i class="fas fa-fw fa-minus"></i>');
      ts.show();
    } else {
      tsi.html('<i class="fas fa-fw fa-plus"></i>');
      $(this).data('status', 0);
      ts.hide();
    }

        if(supports_html5_storage()){
            if(tsi.data('status') == 1)
                localStorage.setItem("montra-search-collapsed", false);
            else
                localStorage.setItem("montra-search-collapsed", true);
        }

  });

  $('#t_search').change(function(){
    $(this).parent().submit();
  });

});

/**
 * Function triggered when user clicks to export all databases on fingerprint listings views
 */
function exportAllFingerprintsCsv(community_slug) {
    bootbox.confirm(
        'Do you want to export all databases? This is a slow process that could take some time, so please be patient.',
        result => {
            if(result) {
                showExportMessage();
                location.assign($('#base_link').attr('href') + `c/${community_slug}/export_all_answers`);
            }
        },
    )
}

/**
 * Fingerprint selection functions
 * @param montra - bool - if the output file must be a montra type file
 * @param community_slug - string - slug of the community. Only required if montra=false
 */
function onShowFingerprintDialog(montra=true, community_slug) {
  if (!a.plugin.getExtraObjects()) {
    return;
  }
  //colect ids
  const aFingerprints = a.plugin.getExtraObjects().selectedList;
  //confirm message
  const plural = aFingerprints.length > 1 ? "s" : "";
  const message = "You are about to export " + aFingerprints.length
                  + " fingerprint" + plural 
                  + ". This is a slow process that can take a couple of minutes. Do you want to continue?"
  //confirm dialog
  bootbox.confirm({
      message: message,
      buttons: {
        confirm: {
            label: 'Yes',
            className: 'btn-primary'
        },
        cancel: {
            label: 'No',
            className: 'btn-light'
        }
      },
      callback: function (result) {
            if (result) {
                if (!community_slug) {
                    console.error("When exporting selected databases you should provide the community slug argument.")
                }

                if (montra) {
                    location.assign(
                        $('#base_link').attr('href')
                        + `c/${community_slug}/export_selected_answers_multimontra`
                        + `?fingerprints=${aFingerprints}`
                    );
                }
                else {
                    location.assign(
                        $('#base_link').attr('href')
                        + `c/${community_slug}/export_selected_answers`
                        + `?fingerprints=${aFingerprints}`
                    );
                }
            }
      }
    }
  );
}
