#!/bin/bash
xhost +
docker run --name app -ti --privileged --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix app 
./attach.sh
