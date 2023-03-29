#!/bin/sh

cp /deploy/catalogue/docker/local_settings.py /deploy/catalogue/emif/emif/

CATALOGUE_ENV=$BASE_DIR

echo $DOCKER_POSTGRES_HOST:$DOCKER_POSTGRES_PORT:*:$DOCKER_POSTGRES_USER:$DOCKER_POSTGRES_PASS > /root/.pgpass
chmod 600 /root/.pgpass


check_up() {
    service=$1
    host=$2
    port=$3

    max=100 # 1 minute

    counter=1
    while true;do
        python -c "import socket;s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);s.connect(('$host', $port))" \
        >/dev/null 2>/dev/null && break || \
        echo "Waiting that $service on $host:${port} is started (sleeping for 5) on counter ${counter}"

        if [ $counter = $max ]; then
            echo "Could not connect to ${service} after some time"
            echo "Investigate locally the logs with fig logs"
            exit 1
        fi

        sleep 5

        counter=$((counter + 1))
    done
}

check_up "postgres" $DOCKER_POSTGRES_HOST $DOCKER_POSTGRES_PORT
check_up "solr" $SOLR_HOST $SOLR_PORT
check_up "memcached" $MEMCACHED_HOST $MEMCACHED_PORT
check_up "mongoDB" $MONGODBHOST $MONGODBPORT


echo "let's log"
mkdir -p /deploy/catalogue/emif/advancedsearch/static
echo "Applying migrations..."
LC_ALL=C cd /deploy/catalogue/emif && python manage.py makemigrations
LC_ALL=C cd /deploy/catalogue/emif && python manage.py migrate


LC_ALL=en_GB.UTF-8 cd /deploy/catalogue/emif && python manage.py check_permissions
if [ "$NEW_INSTALLATION" = "True" ]; then
  echo "Loading initial data..."
  LC_ALL=C cd /deploy/catalogue/docker && sh new_installation.sh
fi


LC_ALL=C cd /deploy/catalogue/emif && python manage.py collectstatic --noinput
LC_ALL=C cd /deploy/catalogue/emif && python manage.py compress --force
# cd /deploy/catalogue/emif && python manage.py set_urls "$PUBLIC_IP$BASE_DIR/static/" "$PUBLIC_IP$BASE_DIR/"
cd /deploy/catalogue/emif && python manage.py set_urls "$PUBLIC_IP/$BASE_DIR/static/" "$PUBLIC_IP/$BASE_DIR/"


echo "Starting celery worker ..."
rm -f /deploy/catalogue/emif/celeryd.pid
if [ -n "$*" ] && [ -n "$DEBUG_CELERY" ] && ! [ "$DEBUG_CELERY" = 0 ] ; then
  "$@" &
else
  cd /deploy/catalogue/emif && C_FORCE_ROOT=True celery -A emif.celery worker -l debug -B -D -f celery.log
fi


if [ "$DEBUG_RUN" = "True" ]; then
  # On debug mode, the base_url will be http://localhost:<debug_mode_port> without any suffix.
  base_url=http://localhost:$DEBUG_MODE_PORT
  cd /deploy/catalogue/emif && sed -i '/"base_url":/c\  "base_url": "'$base_url'",' package.json

  echo "Running npm..."
  cd /deploy/catalogue/emif && npm install

  # On debug mode, use runserver to run the application and serve it on 0.0.0.0:<debug_mode_port>.
  echo "Starting server..."
  if [ -n "$*" ] && [ -n "$DEBUG_DJANGO" ] && ! [ "$DEBUG_DJANGO" = 0 ] ; then
    "$@" &
  else
    cd /deploy/catalogue/emif && python manage.py runserver 0.0.0.0:$DEBUG_MODE_PORT &
  fi
else
  # On production mode, use uwsgi to run the application

  # If the PUBLIC_IP environment variable is not set, the public ip is http://localhost:<production_mode_port>.
  # Otherwise, use the PUBLIC_IP environment variable.
  if [ -z "${PUBLIC_IP}" ]; then
      if [ "$TEST_MODE" = "True" ]; then
        pub_ip="http://nginx:$PRODUCTION_MODE_PORT"
      else
        pub_ip="http://localhost:$PRODUCTION_MODE_PORT"
      fi
  else
    pub_ip="${PUBLIC_IP}"
  fi

  # If the BASE_DIR environment variable is not set, the base_url is the public ip without any suffix.
  # Otherwise, the base_url is the public ip with the suffix that comes from the BASE_DIR environment variable.
  if [ -z "${BASE_DIR}" ]; then
    base_url=$pub_ip
  else
    base_url=$pub_ip/${BASE_DIR}
  fi

  cd /deploy/catalogue/emif && sed -i '/"base_url":/c\  "base_url": "'$base_url'",' package.json

  echo "Starting server using uwsgi..."
  uwsgi --ini /etc/uwsgi/apps-enabled/catalogue.ini

  echo "Running npm..."
  cd /deploy/catalogue/emif && npm install && npm run build

  echo "Collecting webpack-bundle static file..."
  cd /deploy/catalogue/emif && python manage.py collectstatic --noinput
  cd /deploy/catalogue/emif && python manage.py compress --force
  cd /deploy/catalogue/emif && cp -r django_js_reverse/ emif/collected-static/
fi


if [ "$LOAD_TEST_DATA" = "True" ]; then
  echo "Loading test data..."
  cd /deploy/catalogue/emif && ./reset_test_data.sh
fi

if [ "$RUN_TESTS" = "True" ]; then
  echo "Running tests..."
  cd /deploy/catalogue/tests/units && python run_tests.py -hl -b $base_url

  cd /deploy/catalogue/tests/units && python run_tests.py -hl -b $base_url -l
fi


if [ "$DEBUG_RUN" = "True" ]; then
    # This is here to allow real-time compilation for developers.
    cd /deploy/catalogue/emif && exec npm run watch
else
    exec tail -f /dev/null
fi
