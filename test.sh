#!/bin/bash

function img {
    echo "-----------------"
    echo "running img tests"
    echo "-----------------"
    ./rjg.py img || exit
    echo "-----------------"
    ./rjg.py img --nglitch 10 || exit
}

function vid {
    echo "-----------------"
    echo "running vid tests"
    echo "-----------------"
    ./rjg.py vid || exit
}

function all {
    echo "running all tests"
    img
    vid
}

function usage {
    echo "runn: img, via or all"
}

if [ "$1" == "" ]; then
    usage
elif [ "$1" == "all" ]; then
    all
elif [ "$1" == "vid" ]; then
    vid
elif [ "$1" == "img" ]; then
    img
fi


./clean.sh

