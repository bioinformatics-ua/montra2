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
//##########################IMPORTANT
advValidator.searchMode(true);
//###################################

$(".chosen-select").chosen({max_selected_options: 5});


function selectAll(obj, v){
    var ipts = $('[id="'+v+'"]').find('input:checkbox');

    ipts.each(function(e){
        $(this).click(); //prop('checked', !$(this).prop('checked'));
    });
}
