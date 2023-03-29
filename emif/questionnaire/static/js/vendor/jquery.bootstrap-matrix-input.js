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

(function($) {
    $.fn.matrixinput = function(options){
         var self = this;

         var settings = $.extend({
            delete_color: "#000000",
            advanced: false,
            settings: {}
        }, options );

        // You know its gonna happen
        if(!this.is('input') && this.attr('type') != 'text'){
            console.error('Tried to add matrix input to something that is not a text input');
        }
        var serialization;
        try{
            serialization = JSON.parse(this.val());
        } catch(err){
            serialization = {};
        }
        var rId = Math.random().toString(36).substring(7);
        this.hide();


        // Turn an option into a slug. This is necessary to support schema changes along the time
        // Altough its slower than simply using the x and y indexes.
        var __simplex = function(str){
            var tmp = str.toLowerCase().replace(/(<([^>]+)>)/ig, '').replace(/([^a-z0-9])/gi, '');

            console.log(tmp);

            return tmp;
        };

        var config = settings.data;

        var __renderTable = function __renderTable(){
            var __renderHeader = function(config){
                var tmp = [];

                for(var i=0;i<config.x.length;i++){
                    tmp.push('<th><center>'+config.x[i]+'</center></th>');
                }
                if(config.comment){
                    tmp.push('<th>'+config.commentlabel+'</th>');
                }
                return tmp.join('');

            };

            var __renderLine = function(y, xlen, config){
                var tmp = [];

                for(var i=0;i<config.x.length;i++){
                    var this_x = __simplex(config.x[i]);
                    var this_y = __simplex(y);

                    if(config.blocked){
                        tmp.push('<td><center>\
                                <div name="line_'+this_y+'" id="c_'+this_x+'_'+this_y+'" data-x="'+config.x[i]+'" data-y="'+y+'" class="matrixcell">\
                                </div></center></td>');
                    }
                    else {
                        switch(config.type){
                            case 'choice':
                                tmp.push('<td><center>\
                                    <input type="radio" name="line_'+this_y+'" id="c_'+this_x+'_'+this_y+'" value="'+this_x+'" data-x="'+config.x[i]+'" data-y="'+y+'" class="matrixcell" />\
                                    </center></td>');
                            break;

                            case 'checkbox':
                                tmp.push('<td><center>\
                                    <input type="checkbox" name="line_'+this_y+'" id="c_'+this_x+'_'+this_y+'" value="'+this_x+'" data-x="'+config.x[i]+'" data-y="'+y+'" class="matrixcell" />\
                                    </center></td>');
                            break;

                            case 'text':
                                tmp.push('<td><center>\
                                    <textarea name="line_'+this_y+'" id="c_'+this_x+'_'+this_y+'" data-x="'+config.x[i]+'" data-y="'+y+'" class="form-control matrixcell"></textarea>\
                                    </center></td>');
                            break;

                            default:
                            console.log('TYPE OF TABLE IS INVALID');
                            break;
                        }
                    }

                }
                if(config.comment){
                    if(config.blocked){
                        tmp.push('<td><div class="matrixopt" type="text" data-y="'+y+'" name="line'+this_y+'_opt" id="line'+this_y+'_opt"></div></td>');
                    }
                    else {
                        tmp.push('<td><textarea class="form-control matrixopt" type="text" data-y="'+y+'" name="line'+this_y+'_opt" id="line'+this_y+'_opt"></textarea></td>');
                    }
                }

                console.log(tmp);
                return tmp.join('');
            };

            var __renderLines = function(config){
                var tmp = [];
                var xlen = config.x.length;

                for(var i=0;i<config.y.length;i++){
                    tmp.push(
                        '<tr>'+
                            '<td>'+config.y[i]+'</td>'+
                            __renderLine(config.y[i], xlen, config)+
                        '</tr>');
                }
                return tmp.join('');

            };

            return '\
            <table class="qtable table table-bordered table-striped">\
                <thead>\
                    <tr><th><div style="float: right">'+config.xlabel+'</div><div style="clear:both;">'+config.ylabel+'</div></th>'+__renderHeader(config)+'</tr>\
                </thead>\
                <tbody>\
                    '+__renderLines(config)+'\
                </tbody>\
            </table>\
            ';
        };

        var __fillAnswers = function(config){
            for(var i=0;i<config.answers.length;i++){
                var answer = config.answers[i];

                if(answer.x){

                    if(config.blocked){
                        $('#c_'+__simplex(answer.x)+'_'+__simplex(answer.y), '#m_'+rId).html(answer.val);
                    }
                    else {
                        switch(config.type){
                            case 'text':
                                $('#c_'+__simplex(answer.x)+'_'+__simplex(answer.y), '#m_'+rId).val(answer.val);
                                break;
                            case 'checkbox': case 'choice':
                                $('#c_'+__simplex(answer.x)+'_'+__simplex(answer.y), '#m_'+rId).attr('checked', answer.val);
                                break;
                            default: 
                            // break
                            break;
                        }
                    }
                }

                if(config.comment){
                    if(!config.blocked){
                        $('#line'+__simplex(answer.y)+'_opt', '#m_'+rId).val(answer.extra);
                    }
                    else {
                        $('#line'+__simplex(answer.y)+'_opt', '#m_'+rId).html(answer.extra);
                    }

                }
            }
        };
        this.siblings().remove();
        var wrap = this.wrap('<div id="m_'+rId+'" class="matrixinput">'+__renderTable(settings)+'</div>');

        __fillAnswers(config);
        var __handleChanges = function(config, target){
            var target_x, target_y, new_ans, answer, i, val, changed;
            switch(config.type){
                case 'choice':
                    target_x = target.data('x');
                    target_y = target.data('y');

                    new_ans = [];

                    for(i=0;i<config.answers.length;i++){
                        answer = config.answers[i];

                        if(answer.y !== target_y || answer.extra){
                            new_ans.push(answer);
                        }
                    }

                    new_ans.push({
                        x: target_x,
                        y: target_y,
                        val: true
                    });

                    config.answers = new_ans;

                    break;

                case 'checkbox':
                    target_x = target.data('x');
                    target_y = target.data('y');

                    val = target.is(':checked');

                    changed = false;

                    for(i=0;i<config.answers.length;i++){
                        answer = config.answers[i];

                        if((answer.y === target_y && answer.x === target_x)){
                            changed = true;

                            answer.val = val;
                        }
                    }
                    if(!changed){
                        config.answers.push({
                            x: target_x,
                            y: target_y,
                            val: val
                        });
                    }

                    break;

                case 'text':
                    target_x = target.data('x');
                    target_y = target.data('y');

                    val = target.val();

                    changed = false;

                    for(i=0;i<config.answers.length;i++){
                        answer = config.answers[i];

                        if((answer.y === target_y && answer.x === target_x)){
                            changed = true;

                            answer.val = val;
                        }
                    }
                    if(!changed){
                        config.answers.push({
                            x: target_x,
                            y: target_y,
                            val: val
                        });
                    }
                    break;

                default:
                    console.error('UNSSUPORTED TABLE TYPE: '+config.type);
                    break;
            }
        };

        if(config.type == 'text'){
            $('.matrixcell', $(this).parent()).change(function(obj){
                __handleChanges(config, $(obj.target));
                $(self).trigger('matrix:change', [config, obj.target]);

            });
        } else {
            $('.matrixcell', $(this).parent()).click(function(obj){
                __handleChanges(config, $(obj.target));
                $(self).trigger('matrix:change', [config, obj.target]);

            });
        }

        $('.matrixopt', $(this).parent()).change(function(obj){
            var target_y = $(obj.target).data('y');
            var update = false;
            for(var i=0;i<config.answers.length;i++){
                var answer = config.answers[i];
                if(answer.y === target_y && answer.extra){
                    var val = $(obj.target).val();
                    answer.extra = val;
                    update=true;
                }
            }
            if(!update){
                config.answers.push({
                    y: target_y,
                    extra: $(obj.target).val()
                });
            }

            $(self).trigger('matrix:change', [config, obj.target]);

        });
        $(self).val(JSON.stringify(config.answers));


            if(config.blocked){
                setTimeout(function(){
                    $('input, textarea', '#m_'+rId).attr('disabled', true);
                }, 100);
            }


        return self;

    }

}(jQuery));
