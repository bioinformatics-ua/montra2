from community.models import Community, CommunityUser

from django.contrib.auth.models import User
from django.db import transaction

import json, io

@transaction.atomic
def readMap():
    with io.open('interest_to_comm_translation.json', encoding='utf-8') as json_data:
        umap = json.load(json_data)
        json_data.close()

        for email, comms in umap.items():
            user = User.objects.filter(email=email)

            if len(user) > 0:
                for comm in comms:
                    fu = user[0]

                    fu.emif_profile.restricted = False
                    fu.emif_profile.save()

                    community = Community.objects.get(slug=comm)

                    cu = CommunityUser(user=fu, community=community, status=CommunityUser.ENABLED)

                    cu.save()

readMap()


