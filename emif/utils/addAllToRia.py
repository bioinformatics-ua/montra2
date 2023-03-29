from django.contrib.auth.models import User
from community.models import Community, CommunityUser
from django.db import transaction


@transaction.atomic
def add():
    ria = Community.objects.get(slug='ria')
    everyone = User.objects.all()

    for user in everyone:

        cu = CommunityUser.objects.get_or_create(community = ria, user=user, status=CommunityUser.ENABLED)

add()
