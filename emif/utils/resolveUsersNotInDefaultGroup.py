from community.models import Community, CommunityGroup, CommunityUser
from django.db import transaction
from django.conf import settings
from emif.tasks import send_custom_mail


@transaction.atomic
def resolve_users_not_in_default_group(send_mail=False):
    """
    This function scans all existing communities in order to detect community users that are NOT in the default group
        ("outcasts", if you will) of their respective communities. Once found, these users are automatically added to
        their respective groups. This happened due to a prior bug in Montra.
    """

    print "Resolving default user outcasts..."

    mails_to_send = []

    for community in Community.objects.all():
        default_group = CommunityGroup.objects.filter(name="default", community=community)
        if default_group.count() > 1:
            # if there is a removed default group, move all its members to the active one and delete the removed group
            removed = default_group.get(removed=True)
            active = default_group.get(removed=False)
            for user in removed.members.all():
                active.members.add(user)
            removed.delete()
            default_group = active
        else:
            default_group = default_group.get()

        community_users = CommunityUser.objects.filter(community=community, status=CommunityUser.ENABLED)
        outcasts = community_users.exclude(id__in=default_group.members.all())

        print("[%s] - %d users are not in the default group." % (community.name, len(outcasts)))

        for outcast in outcasts:
            print "\tAdding " + outcast.user.first_name + "..."
            default_group.members.add(outcast)

        if send_mail and community.membership not in (community.MEMBERSHIP_OPEN, community.MEMBERSHIP_INVITATION):
            for outcast in outcasts:
                mails_to_send.append((outcast.user.get_full_name(), community.name, outcast.user.email))

    for name, comm_name, email in mails_to_send:
        send_custom_mail.delay(
            '{}: Fixed data access to {}'.format(settings.GLOBALS['BRAND'], comm_name),
            """Dear {},

The correct permissions were not given when you joined the community {}, which may have caused you issues when accessing data in the website.
We have resolved this issue and you should now be able to use the website normally.

We are sorry for the inconvenience.

Sincerely,
{}
""".format(name, comm_name, settings.GLOBALS['BRAND']),
            settings.DEFAULT_FROM_EMAIL,
            [email],
        )
