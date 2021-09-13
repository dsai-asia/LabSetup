#!/bin/bash

cd "`dirname $0`"/..

./bin/buildit.sh

./bin/stopit.sh

docker-compose --env-file .env up > jupyter.log 2>&1 &

