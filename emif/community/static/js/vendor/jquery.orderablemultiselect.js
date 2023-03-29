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
    $.fn.orderablemultiselect = function( options ) {
        var self = this;
        var hash = Math.random().toString(36).slice(2);
        var sortable1, sortable2;
        var selected = null;

        var settings = $.extend({
            fromtext: 'Selected',
            totext: 'Available',
            from: [],
            to: [],
            change: undefined,
            
        }, options );

        var public_funcs = {
            serialization(){
                return {
                    from: settings.from.filter(obj => obj.id && !obj.disabled),
                    to: settings.to
                };
            }
        };

        var render_icon = function(icon){
            return '<span>  | </span><span class="' + icon + '"></span>';
        }

        var render_line_icon_label = function(value){
            return ( settings.selectShowLabel && value ? render_icon('fas fa-fw fa-tag') : '' );
        }

        var render_line_icon_icon = function(value){
            return ( settings.selectIcon && value ? render_icon(value) : '' );
        }

        var renderLines = function(array){
            returnable ='';
            for(var i=0;i<array.length;i++){
                var line = array[i];
                returnable += '<li title="'+line.name+'" data-value="'+line.id+'" data-serialization="'+btoa(JSON.stringify(line))+'" class="btn '+ (line.disabled? 'btn-grey': 'btn-blue') +
                                    ' btn-xs btn-block">'+line.name
                                + '<span class="line-label">'
                                + render_line_icon_label(line.label)
                                +'</span>'
                                + '<span class="line-icon">'
                                + render_line_icon_icon(line.icon)
                                +'</span>'
                                +'</li>';
            }

            return returnable;
        };

        var render = function(){
            var returnable;
            returnable = '\
                <div class="col-xs-6">\
                <strong>'+settings.fromtext+'</strong>\
                <div class="well well-sm">\
                  <ul class="sortable1 listsorter list-unstyled connectedSortable">';

            returnable += renderLines(settings.from);

            returnable += '</ul>\
                </div>\
                </div>\
                <div class="col-xs-6">\
                <strong>'+settings.totext+'</strong>\
                <div class="well well-sm"><ul class="sortable2 listsorter list-unstyled connectedSortable">';

            returnable += renderLines(settings.to);

            returnable += '</ul>\
                </div>\
                </div>';

            returnable += '<div class="modal fade" tabindex="-1" role="dialog">\
            <div class="modal-dialog" role="document">\
              <div class="modal-content">\
                <div class="modal-header">\
                  <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>\
                  <h4 class="modal-title"></h4>\
                </div>\
                <div class="modal-body">\
                    <div class="form-group">\
                        <label for="name">Field:</label>\
                        <span class="form-control field-name"><span>\
                    </div>\
                    <div class="form-group">\
                        <label>Icon:</label>\
                        <input class="form-control field-icon">\
                    </div>\
                    <div class="checkbox">\
                        <label><input type="checkbox" value="" class="field-showlabel">Show label</label>\
                    </div>\
                    <div class="checkbox">\
                        <label><input type="checkbox" value="" class="field-applyformatting">Apply Formatting <small>(Example: show \'5000\' as \'5.0K\')</small></label>\
                    </div>\
                </div>\
                <div class="modal-footer">\
                  <button type="button" class="btn btn-transparent" data-dismiss="modal">Close</button>\
                  <button type="button" class="btn btn-primary button-save">Save</button>\
                  <button type="button" class="btn btn-primary button-add">Add</button>\
                  <button type="button" class="btn btn-danger button-remove">Remove</button>\
                </div>\
              </div><!-- /.modal-content -->\
            </div><!-- /.modal-dialog -->\
          </div><!-- /.modal -->'

            return returnable;
        };

        var evaluateUls = function(evt, ui){
            var handler, children, target = [];

            if($.isWindow(this)){
                handler=$(evt);
            } else {
                handler=$(this);
            }

            children = handler.children();

            for(var i=0;i<children.length;i++){
                target.push(JSON.parse(atob($(children[i]).data('serialization'))));
            }

            if(handler.hasClass('sortable1')){
                settings.from = target;
            } else {
                settings.to = target;
            }

            if(settings.change){
                settings.change(public_funcs.serialization());
            }
        };

        var s1_handler = function(evt){
                selected = $(this);
                const data = JSON.parse(atob(selected.data('serialization')));
                if(settings.selectShowLabel || data.type === "numeric" || settings.selectIcon){
                    dialog('Field details', data, 'show');
                }else{
                    remove(selected);
                }            
        };

        var s2_handler = function(evt){
                selected = $(this);
                const data = JSON.parse(atob(selected.data('serialization')));
                if(settings.selectShowLabel || data.type === "numeric" || settings.selectIcon){
                    dialog('Add Field', data, 'add');
                }else{
                    add(selected);
                }              
        };

        var add = function(){
            sortable1.append(selected);
            selected.click(s1_handler);
            evaluateUls(sortable1[0]);
            evaluateUls(sortable2[0]);
        }

        var remove = function(){
            selected.remove();
            selected.find('span').remove();
            sortable2.append(selected);
            selected.click(s2_handler);
            evaluateUls(sortable1[0]);
            evaluateUls(sortable2[0]);
        }

        var update_selected_line_icons = function(label, icon){
            //update icons
            selected.find('.line-label').html(render_line_icon_label(label))
            selected.find('.line-icon').html(render_line_icon_icon(icon))
        }

        var dialog = function(sTitle, data, mode) {
            var m = $(self).find('.modal');

            //get controllers
            var oIcon = m.find('.field-icon');
            var oShowLabel = m.find('.field-showlabel');
            var oApplyFormatting = m.find('.field-applyformatting');
            var oBtnSave = m.find('.button-save');
            var oBtnRemove = m.find('.button-remove');
            var oBtnAdd = m.find('.button-add');

            //set operations
            oBtnAdd.click(function(){
                data.icon = oIcon.val();
                data.label = oShowLabel.prop('checked');
                data.formatting = oApplyFormatting.prop('checked');
                //update serialize data fields
                selected.data('serialization', btoa(JSON.stringify(data)))
                //update icons
                update_selected_line_icons(data.label, data.icon)
                //add selected element
                evaluateUls(sortable2[0]);
                add();
                m.modal('hide');
            });

            oBtnSave.click(function(){
                data.icon = oIcon.val();
                data.label = oShowLabel.prop('checked');
                data.formatting = oApplyFormatting.prop('checked');
                //update serialize data fields
                selected.data('serialization', btoa(JSON.stringify(data)))
                //update icons
                update_selected_line_icons(data.label, data.icon)
                //update form content
                evaluateUls(sortable1[0]);
                m.modal('hide');
            });

            oBtnRemove.click(function(){
                remove();
                m.modal('hide');
            });

            //set dialog properties
            m.find('.modal-title').text(sTitle);
            m.find('.field-name').text(data.name);
            m.find('.field-icon').val(data.icon);    
            m.find('.field-showlabel').prop('checked', data.label);
            m.find('.field-applyformatting').prop('checked', data.formatting);

            //set dialog controllers according to mode property
            //and settings
            if(!settings.selectShowLabel){
                oShowLabel.parent().hide();
            }

            if(data.type !== "numeric"){
                oApplyFormatting.parent().hide();
            }
            else {
                oApplyFormatting.parent().show();
            }

            if(!settings.selectIcon){
                oIcon.parent().hide();
            }

            if(mode === 'add'){
                oBtnSave.hide();
                oBtnRemove.hide();
                oBtnAdd.show();
            }else{
                oBtnSave.show();
                oBtnRemove.show();
                oBtnAdd.hide();
            }

            //open modal
            m.modal('show');
        }

        var applyOrderable = function(){
            $( ".sortable1, .sortable2", self).sortable({
                connectWith: ".connectedSortable",
                zIndex: 9999,
                cancel: ".btn-grey",
                update: evaluateUls
            }).disableSelection();
        };

        self.html(render());

        //apply icon selector
        var options = {
            fullClassFormatter: function(val) {
                return 'fa ' + val;
            },
            selectedCustomClass: 'bg-primary', // Appends this class when to the selected item
            templates: {
                popover: '<div class="iconpicker-popover popover"><div class="arrow"></div>' +
                    '<div class="popover-title"></div><div class="popover-content"></div></div>',
                footer: '<div class="popover-footer"></div>',
                buttons: '<button class="iconpicker-btn iconpicker-btn-cancel btn btn-default btn-sm">Cancel</button>' +
                    ' <button class="iconpicker-btn iconpicker-btn-accept btn btn-primary btn-sm">Accept</button>',
                search: '<input type="search" class="form-control iconpicker-search" placeholder="Type to filter" />',
                iconpicker: '<div class="iconpicker"><div class="iconpicker-items"></div></div>',
                iconpickerItem: '<a role="button" class="iconpicker-item"><i></i></a>',
            }
        };

        try {
            $('.field-icon').iconpicker(options);
        } catch (error) {
            console.log(error)    
        }

        sortable1 = $('.sortable1', self);
        sortable2 = $('.sortable2', self);

        applyOrderable();

        $('.sortable1 li:not(.btn-grey)', self).click(s1_handler);
        $('.sortable2 li:not(.btn-grey)', self).click(s2_handler);

        return public_funcs;

    };
}( jQuery ));
