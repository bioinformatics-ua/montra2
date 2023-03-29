#!/bin/sh
echo "Loading initial data..."
cd /deploy/catalogue/emif && (
    python manage.py loaddata fixtures/initial_profile.json
    python manage.py loaddata fixtures/initial_groups.json
    python manage.py create_user --superuser admin bastiao@ua.pt emif
    python manage.py create_user demo bastiao2@ua.pt catalogue

    # Change flatpages wordpress url placeholder
    sed s^"{WORDPRESS_PREFIX}"^$WORDPRESS_PREFIX^ fixtures/flatpages_with_placeholders.json > fixtures/flatpages.json
    python manage.py loaddata fixtures/flatpages.json
)
