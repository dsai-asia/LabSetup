#!/bin/bash

cd "`dirname $0`"

docker-compose down || {
    echo "Service may be stopped already"
    exit 0
}

