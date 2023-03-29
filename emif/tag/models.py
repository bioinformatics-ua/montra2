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
from django.db import models

# Generic tag model, to be reused by all applications like community and databases eventually
class Tag(models.Model):
    slug = models.CharField(max_length=100)
    desc = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        ordering = ['slug']

    @staticmethod
    def parse_tags(string):
        tags = []

        if string and isinstance(string, basestring):

            words = string.strip().lower().split(',')

            for word in words:
                clean_word = word.strip()
                tags.append(Tag.create_or_get(clean_word))

        return tags

    @staticmethod
    def create_or_get(slug):
        the_slug = None

        if isinstance(slug, Tag):
            the_slug = slug.slug

        elif isinstance(slug, basestring):
            the_slug = slug


        try:
            tt = Tag.objects.get(slug=the_slug)

            return tt

        except Tag.DoesNotExist:
            tt = Tag(slug = the_slug)

            tt.save()

            return tt

