# simple makefile to simplify repetetive build env management tasks under posix

CTAGS ?= ctags

all: clean inplace test

clean-pyc:
	@find . -name "*.pyc" | xargs rm -f

clean-so:
	@find . -name "*.so" | xargs rm -f
	@find . -name "*.pyd" | xargs rm -f

clean-build:
	@rm -rf build

clean-ctags:
	@rm -f tags

clean-cache:
	@find . -name "__pycache__" | xargs rm -rf

clean: clean-build clean-pyc clean-so clean-ctags clean-cache
	@echo "Cleaning build, pyc, so, ctags, and cache"

clean-test: clean-build clean-pyc clean-ctags clean-cache
	@echo "Cleaning build, pyc, ctags, and cache"

in: inplace # just a shortcut
inplace:
	python setup.py build_ext -i

nosetests: nose # alias

# Test conditions, don't "clean-so" or builds won't work!

nose: clean-test
	python make test nose

nose_coverage: clean-test
	python make test nose 1

coverage_html:
	python make coverage_html

test: clean-test
	python make test full

flake: clean-test
	python make test flake

flake3: clean-test
	python3 make test flake

lineendings: clean-test
	python make test lineendings

extra: clean-test
	python make test extra

nobackend : clean-test
	python make test nobackend

pyqt4: clean-test
	python make test pyqt4

pyside: clean-test
	python make test pyside

pyglet: clean-test
	python make test pyglet

glfw: clean-test
	python make test glfw

sdl2: clean-test
	python make test sdl2

glut: clean-test
	python make test glut

ipynb_vnc: clean-test
	python make test ipynb_vnc
