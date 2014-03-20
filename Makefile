# simple makefile to simplify repetetive build env management tasks under posix

# caution: testing won't work on windows, see README

PYTHON ?= python
CTAGS ?= ctags

all: clean inplace test

clean-pyc:
	find . -name "*.pyc" | xargs rm -f

clean-so:
	find . -name "*.so" | xargs rm -f
	find . -name "*.pyd" | xargs rm -f

clean-build:
	rm -rf build

clean-ctags:
	rm -f tags

clean: clean-build clean-pyc clean-so clean-ctags

flake:
	python make flake

in: inplace # just a shortcut
inplace:
	$(PYTHON) setup.py build_ext -i

nosetests: nose # alias
nose:
	python make nose

test: clean
	python make test

lineendings: clean
	python make lineendings

