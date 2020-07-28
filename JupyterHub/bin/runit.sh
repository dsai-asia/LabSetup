#!/bin/bash

cd "`dirname $0`"/..

./bin/buildit.sh

./bin/stopit.sh

docker-compose up > jupyter.log 2>&1 &

