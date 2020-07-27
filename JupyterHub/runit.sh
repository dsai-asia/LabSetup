#!/bin/bash

cd "`dirname $0`"

./buildit.sh

./stopit.sh

docker-compose up > jupyter.log 2>&1 &

