from community.models import Community

def fixPermissions():
    cs = Community.objects.all()

    for c in cs:
        c.public = False

        c.save()

fixPermissions()
