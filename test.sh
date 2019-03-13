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
    echo "-----------------"
    ./rjg.py vid --fps=10 --rounds=20 --steps-per-round=10 --glitch-per-step=2
    echo "-----------------"
}

function all {
    echo "running all tests"
    img
    vid
}

function usage {
    echo "uage: ./test.sh [img, via, all]"
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

