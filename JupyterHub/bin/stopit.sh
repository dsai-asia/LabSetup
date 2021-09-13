#!/bin/bash

cd "`dirname $0`"/..

docker-compose --env-file .env down || {
    echo "Service may be stopped already"
    exit 0
}

