from accounts.models import EmifProfile

from django.contrib.auth.models import User

import json, io

translationMap = {
    'observationaldatasources': 'observational',
    'adcohort': 'adcohort',
    'epad': 'epad'
}

def buildMap():
    users_map = {}

    users = User.objects.all()

    for user in users:
        if user.id != -1:
            user_map = []
            interests = user.emif_profile.interests.all()

            for interest in interests:
                translation = translationMap.get(interest.slug, 'ERROR')

                if translation != 'ERROR':
                    user_map.append(translation)
                #else:
                #    print "DO NOT KNOW %s" % (interest.slug)

            users_map[user.email] = user_map

    with io.open('interest_to_comm_translation.json', 'w', encoding='utf-8') as f:
        f.write(unicode(json.dumps(users_map, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))))

buildMap()
