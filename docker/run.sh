#!/bin/bash

echo "Running Docker.. "

docker-compose down
docker-compose up -d --no-recreate
