#!/bin/bash

cd "`dirname $0`"/..

./bin/buildit.sh

docker-compose --env-file .env up -d

