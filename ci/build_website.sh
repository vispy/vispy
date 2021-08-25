#!/usr/bin/env bash
# Build sphinx documentation

# Make "main" the tag so the website gets deployed
# The website deployment checks for any tags by checking
# this variable.
export TRAVIS_TAG="main"

cd doc

make clean
# TODO: Switch to sphinx-multiversion
make html SPHINXOPTS="-W --keep-going"
touch _build/html/.nojekyll

# move back to source directory so we don't mess with future steps
cd ..
