# -*- coding: utf-8 -*-
# Copyright (C) 2016 BMD software
#
# Author: Luís A. Bastião Silva <bastiao@bmd-software.com>
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

import recaptcha2


"""This is the recaptch module 
"""
class Recaptcha(object):

    def __init__(self, publicDomain, publicKey, privateKey ):
        self.publicKey = publicKey
        self.privateKey = privateKey
        self.publicDomain = publicDomain

    
    def verify(self, response):
        result = recaptcha2.verify(self.privateKey, response, self.publicDomain)
        return result['success']


