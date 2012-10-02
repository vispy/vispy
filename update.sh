#!/bin/bash

# quit on any error
set -e

git pull origin master
git submodule init
git submodule update

