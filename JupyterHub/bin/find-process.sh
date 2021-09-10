#!/bin/bash

cd "`dirname $0`"/..

if [ "$1" == "" ] ; then
  echo "Usage: $0 <PID>"
  exit 1
fi

PID=$1
echo "Finding process $PID"

CONTAINERS=`docker ps | cut -f1 -d' '`

for CONTAINER in $CONTAINERS ; do
  if [ "$CONTAINER" == "CONTAINER" ] ; then
    continue
  fi
  echo "Container $CONTAINER..."
  RES=`docker top $CONTAINER | sed 's/  */\t/g' | cut -f2 | grep "^${PID}\$"`
  if [ "$RES" == "" ] ; then
    echo "None"
  else
    echo "Some:"
    docker top $CONTAINER
  fi 
  #echo $RES
done

