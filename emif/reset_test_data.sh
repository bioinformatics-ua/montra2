#!/bin/bash

if [ "$TEST_MODE" = "True" ]; then
    python manage.py flush --noinput
    python manage.py loaddata fixtures/test_fixtures/termsconditions.json
    python manage.py loaddata fixtures/test_fixtures/users.json
    python manage.py loaddata fixtures/test_fixtures/profiles.json
    python manage.py loaddata fixtures/test_fixtures/sites.json
    python manage.py loaddata fixtures/test_fixtures/flatpages.json
    python manage.py loaddata fixtures/test_fixtures/initial_groups.json
    python manage.py loaddata fixtures/test_fixtures/community.json
    printf "from community.models import Community
for c in Community.objects.all():
    c.save()
" | python manage.py shell  # this will create missing PRE_EXISTING_GROUPs on all Communities
    python manage.py index_all
    python manage.py check_permissions
else
    echo "TEST_MODE is disabled. Operation cancelled."
fi
