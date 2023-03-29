# If the BASE_DIR environment variable is not set, setup nginx using the nginx_root.conf instead of nginx.conf.
if [ -z "$BASE_DIR" ] ; then
    cp /nginx_root.conf.template /etc/nginx/conf.d/default.conf
else
    cp /nginx.conf.template /etc/nginx/conf.d
    sed -i s/"{BASE_PLACEHOLDER}"/$BASE_DIR/g /etc/nginx/conf.d/default.conf
fi

# Change wordpress associated locations to get the configured prefix
sed -i s^"{WORDPRESS_PREFIX}"^$WORDPRESS_PREFIX^ /etc/nginx/conf.d/default.conf

# Set the server listen port in the nginx configuration file to the <production_mode_port>.
sed -i s/"{PRODUCTION_MODE_PORT}"/$PRODUCTION_MODE_PORT/g /etc/nginx/conf.d/default.conf
