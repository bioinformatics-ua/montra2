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
from django.db.models.signals import post_save
from django.dispatch import receiver

from models import Community, CommunityGroup


@receiver(post_save, sender=Community)
def create_base_groups(sender, instance, *args, **kwargs):
    """
    Create mandatory groups
    """
    if kwargs.get("raw", False):
        # When loading fixtures, dont create these groups
        #  as fixture might create them. However, you should call
        #  Community.save() after loading the fixture, so the next
        #  else block executes and creates missing CommunityGroups
        return

    created = kwargs["created"]
    if created:
        # The these groups should always be created.
        CommunityGroup.create_pre_existing_group(CommunityGroup.DEFAULT_GROUP, instance)
        CommunityGroup.create_pre_existing_group(CommunityGroup.EDITORS_GROUP, instance)
        CommunityGroup.create_pre_existing_group(CommunityGroup.STUDY_MANAGERS_GROUP, instance)
        CommunityGroup.create_pre_existing_group(CommunityGroup.API_GROUP, instance)
        CommunityGroup.create_pre_existing_group(CommunityGroup.DATABASE_OWNERS_GROUP, instance)

        instance.sortid = instance.id
        instance.save()
    else:
        # If the community has been modified, for secure we should check if the groups exists
        valid = CommunityGroup.valid(community=instance)

        for group in CommunityGroup.PRE_EXISTING_GROUPS:
            if not valid.filter(name=group).exists():
                CommunityGroup.create_pre_existing_group(group, instance)
