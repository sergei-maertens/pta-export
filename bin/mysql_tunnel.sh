#!/bin/bash

tunnel=$1
target=$2

ssh \
    -4 \
    -fNTL \
    \*:3306:$target:3306 \
    $tunnel
