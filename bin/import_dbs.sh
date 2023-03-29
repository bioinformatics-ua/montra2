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

if [ -z "$1" ]; then
    echo "Usage: $0 some_backup.sql"
    exit 1
fi

LOCATION_SQL=`$1`

TABLES=`docker exec -it  docker_catalogue_1 bash -c "echo \"SELECT string_agg(table_name, ',') FROM information_schema.tables WHERE table_schema='public'\" | psql -h db -U usertest -d TEST_DB -t"`

echo Dropping tables:${TABLES}

docker exec -it  docker_catalogue_1 bash -c "echo \"DROP TABLE IF EXISTS ${TABLES} CASCADE\" | psql -h db -U usertest -d TEST_DB -t"

echo "Sending $1"

docker cp $1 docker_catalogue_1:/tmp/backup.sql
docker exec -it  docker_catalogue_1 bash -c "psql -h db -U usertest -d TEST_DB  < /tmp/backup.sql"

echo "Done"
