#!/bin/bash

cd "`dirname $0`"
./buildit.sh

docker-compose down

docker-compose up > jupyter.log 2>&1 &

