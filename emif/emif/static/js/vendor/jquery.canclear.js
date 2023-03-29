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

(function ( $ ) {
    $.fn.canclear = function( options ) {
         var self = this;

         var settings = $.extend({
            delete_color: "#000000",
            advanced: false,
        }, options );

        // You know its gonna happen
        if(!this.is('input') && this.attr('type') != 'text'){
            console.error('Tried to add cleanability button to something is not a text input');
        }
        // Wrap it up
        else {
            var classes = this.attr('class');
            //this.attr('class', '');
            this.attr('style','float: left; padding-top: -6px; display:inline-block; border: 0px solid #ccc !important; box-shadow: none;-moz-box-shadow: none;-webkit-box-shadow: none;');
            this.wrap('<div style="height: 36px; background-color: white; border: 1px solid #ccc; -webkit-border-radius: 15px; -moz-border-radius: 15px; border-radius: 15px;" class="canclear_outer"></div>');
            if(settings.advanced){
            this.parent().append('\
                <span style="padding-right:10px; float: right; padding-top:7px; cursor: pointer; margin-right: 0px;" class="canclear_search">\
                    <ul style="padding: 0;" class="unstyled-list"><li class="dropdown">\
                    <a href="#" data-toggle="dropdown">\
                       <i class="fas fa-fw fa-bars"></i>\
                    </a>\
                    <div style="padding:0; z-index:1002;" class="dropdown-menu md arrows pull-right panel panel-default arrows-top-right messages-dropdown">\
                        <div style="cursor: default;" class="panel-heading">\
                        Advanced Search\
                        </div>\
                        <span id="dbtypes_placeholder">\
                        </span>\
                        <a href="advsearch/history" class="btn btn-info btn-flat btn-block">My Searches</a>\
                       </span></li></ul>');
            }
            this.parent().append('<span style="padding-right:8px; float: right; padding-top:6px; cursor: pointer; margin-right: 0px;" class="canclear_button"><i class="icon-remove"></i></span>');

            if($(this).val() == ''){
                $(this).parent().children('.canclear_button').fadeTo(600, 0);
            } else {
                $(this).parent().children('.canclear_button').fadeTo(600, 1);
            }
        //-webkit-box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075), 0 0 6px #7ab5d3;-moz-box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075), 0 0 6px #7ab5d3;box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075), 0 0 6px #7ab5d3;
        this.focusin(function() {
          $( self ).parent().parent().css({'-webkit-box-shadow': 'inset 0 1px 1px rgba(0, 0, 0, 0.075), 0 0 6px #7ab5d3', '-moz-box-shadow': 'inset 0 1px 1px rgba(0, 0, 0, 0.075), 0 0 6px #7ab5d3', 'box-shadow': 'inset 0 1px 1px rgba(0, 0, 0, 0.075), 0 0 6px #7ab5d3'});
        });
        this.focusout(function() {
          $( self ).parent().parent().css({'-webkit-box-shadow': 'inset 0 0px 0px rgba(0, 0, 0, 0), 0 0 0px #7ab5d3', '-moz-box-shadow': 'inset 0 0px 0px rgba(0, 0, 0, 0), 0 0 0px #7ab5d3', 'box-shadow': 'inset 0 0px 0px rgba(0, 0, 0, 0), 0 0 0px #7ab5d3'});
        });
        this.on('keyup', function(){
            console.log($(this).val());
            if($(this).val() == ''){
                $(this).parent().children('.canclear_button').fadeTo(300, 0);
            } else {
                $(this).parent().children('.canclear_button').fadeTo(300, 1);
            }
        });
        $(this).parent().children('.canclear_button').click(function(){
            $(self).val('');
            $(this).fadeTo(300, 0);
        });
        $(this).parent().children('.canclear_search').click(function(){
           //$(this).closest('form').submit();
        });

        var dbp = $('#dbtypes_placeholder');
        var community = $('#communityindicator').val();
        $.get("api/dbtypes/"+community)
            .done(function(data) {
                if(data.types){
                    var content = "";
                    var types = data.types;
                    var tlen = types.length;

                    for(var i=0; i<tlen; i++){
                        if(community && community.length > 0)
                            content += '<a href="c/'+community+'/advancedSearch/'+types[i].id+'/1" class="list-group-item">\
                                            <div class="media">\
                                              <div class="media-body">\
                                                <h5 class="media-heading">'+types[i].name+'</h5>\
                                              </div>\
                                            </div>\
                                        </a>';
                        else
                            content += '<a href="advancedSearch/'+types[i].id+'/1" class="list-group-item">\
                                            <div class="media">\
                                              <div class="media-body">\
                                                <h5 class="media-heading">'+types[i].name+'</h5>\
                                              </div>\
                                            </div>\
                                        </a>';
                    }

                    dbp.html(content);

                } else {
                    dbp.html('No databases types available');
                }
            })
            .fail(function() {
                dbp.html('Error retrieving database types');

            });

        }
        return this;

    };
/*
/* (jQ addClass:) if input has value:
.clearable.x{
  background-position: right 5px center;
}
/* (jQ addClass:) if mouse is over the 'x' input area
.clearable.onX{
  cursor:pointer;
}
*/
}( jQuery ));
