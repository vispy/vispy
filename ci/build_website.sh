#!/usr/bin/env bash
# Build sphinx documentation

# Make "master" the tag so the website gets deployed
# The website deployment checks for any tags by checking
# this variable.
export TRAVIS_TAG="master"

cd doc
make clean
# TODO: Fail if warnings from generation
#       make html SPHINXOPTS="-W"
# TODO: Switch to sphinx-multiversion
make html
touch _build/html/.nojekyll
