#!/bin/bash

NUM_WORKERS=10

for (( c=0; c<$NUM_WORKERS; c++ )) 
do
    echo "worker_${c}"
    echo "$(sudo docker container logs worker_${c} | grep 'ExceptionThrown')"
done