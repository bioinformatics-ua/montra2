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
from django.contrib import admin
from django.contrib.auth.models import User
from adminplus.sites import AdminSitePlus

from .models import *

# Too many for inline, inline would need pagination which is not possible by default
#class CommunityUserInline(admin.TabularInline):
#    model = CommunityUser


class TagAdmin(admin.ModelAdmin):
    list_display = ['slug', 'desc']

admin.site.register(Tag, TagAdmin)
