#!/bin/bash

cd "`dirname $0`"/..

./bin/buildit.sh

docker-compose up -d

