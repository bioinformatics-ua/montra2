/*
# -*- coding: utf-8 -*-
# Copyright (C) 2017 BMD software, Lda
#
# Author: Luís A. Bastião Silva <bastiao@bmd-software.com 
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


function Montra() {
    
}

/**
 * Get base URL 
 */
Montra.prototype.getBase = function() {
    // This implementation it is ok (not a better)
    return $('#base_link').prop('href');
};

/**
 * Get base URL for the community 
 */
Montra.prototype.getBaseCommunity = function() {
    // TODO: we need a better implementation ok? 
    // This was just a first try.

    return $('#base_link').prop('href') + 'c/' + $("#communityindicator").val() + '/';
};


Montra.prototype.getCurrentCommunitySlug = function() {
    // TODO: we need a better implementation ok? 
    // This was just a first try.
    return $("#communityindicator").val();
};

// Just create a controller to make it always available. 
var MontraAPI = new Montra();


