#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for mo

"""
Convenience tools for vispy developers

    make.py command [arg]

"""

from __future__ import division, print_function

import sys
import os
from os import path as op
import time
import shutil
import subprocess
import re
import webbrowser
import traceback
import numpy as np

# Save where we came frome and where this module lives
START_DIR = op.abspath(os.getcwd())
THIS_DIR = op.abspath(op.dirname(__file__))

# Get root directory of the package, by looking for setup.py
for subdir in ['.', '..']:
    ROOT_DIR = op.abspath(op.join(THIS_DIR, subdir))
    if op.isfile(op.join(ROOT_DIR, 'setup.py')):
        break
else:
    sys.exit('Cannot find root dir')


# Define directories and repos of interest
DOC_DIR = op.join(ROOT_DIR, 'doc')
#
WEBSITE_DIR = op.join(ROOT_DIR, '_website')
WEBSITE_REPO = 'git@github.com:vispy/vispy-website'
#
PAGES_DIR = op.join(ROOT_DIR, '_gh-pages')
PAGES_REPO = 'git@github.com:vispy/vispy.github.com.git'
#
IMAGES_DIR = op.join(ROOT_DIR, '_images')
IMAGES_REPO = 'git@github.com:vispy/images.git'


class Maker:

    """ Collection of make commands.

    To create a new command, create a method with a short name, give it
    a docstring, and make it do something useful :)

    """

    def __init__(self, argv):
        """ Parse command line arguments. """
        # Get function to call
        if len(argv) == 1:
            func, arg = self.help, ''
        else:
            command = argv[1].strip()
            arg = ' '.join(argv[2:]).strip()
            func = getattr(self, command, None)
        # Call it if we can
        if func is not None:
            func(arg)
        else:
            sys.exit('Invalid command: "%s"' % command)

    def coverage_html(self, arg):
        """Generate html report from .coverage and launch"""
        print('Generating HTML...')
        from coverage import coverage
        cov = coverage(auto_data=False, branch=True, data_suffix=None,
                       source=['vispy'])  # should match testing/_coverage.py
        cov.combine()
        cov.load()
        cov.html_report()
        print('Done, launching browser.')
        fname = op.join(os.getcwd(), 'htmlcov', 'index.html')
        if not op.isfile(fname):
            raise IOError('Generated file not found: %s' % fname)
        webbrowser.open_new_tab(fname)

    def help(self, arg):
        """ Show help message. Use 'help X' to get more help on command X. """
        if arg:
            command = arg
            func = getattr(self, command, None)
            if func is not None:
                doc = getattr(self, command).__doc__.strip()
                print('make.py %s [arg]\n\n        %s' % (command, doc))
                print()
            else:
                sys.exit('Cannot show help on unknown command: "%s"' % command)

        else:
            print(__doc__.strip() + '\n\nCommands:\n')
            for command in sorted(dir(self)):
                if command.startswith('_'):
                    continue
                preamble = command.ljust(11)  # longest command is 9 or 10
                # doc = getattr(self, command).__doc__.splitlines()[0].strip()
                doc = getattr(self, command).__doc__.strip()
                print(' %s  %s' % (preamble, doc))
            print()

    def doc(self, arg):
        """ Make API documentation. Subcommands:
                * html - build html
                * show - show the docs in your browser
        """
        # Prepare
        build_dir = op.join(DOC_DIR, '_build')
        if not arg:
            return self.help('doc')
        # Go
        if 'html' == arg:
            sphinx_clean(build_dir)
            sphinx_build(DOC_DIR, build_dir)
        elif 'show' == arg:
            sphinx_show(op.join(build_dir, 'html'))
        else:
            sys.exit('Command "doc" does not have subcommand "%s"' % arg)

    def website(self, arg):
        """ Build website. Website source is put in '_website'. Subcommands:
                * html - build html
                * show - show the website in your browser
                * upload - upload (commit+push) the resulting html to github
        """
        # Prepare
        build_dir = op.join(WEBSITE_DIR, '_build')
        html_dir = op.join(build_dir, 'html')

        # Clone repo for website if needed, make up-to-date otherwise
        if not op.isdir(WEBSITE_DIR):
            os.chdir(ROOT_DIR)
            sh("git clone %s %s" % (WEBSITE_REPO, WEBSITE_DIR))
        else:
            print('Updating website repo')
            os.chdir(WEBSITE_DIR)
            sh('git pull')

        if not arg:
            return self.help('website')

        # Go
        if 'html' == arg:
            sphinx_clean(build_dir)
            try:
                sphinx_build(WEBSITE_DIR, build_dir)
            except SystemExit as err:
                if err.code:
                    raise
            sphinx_copy_pages(html_dir, PAGES_DIR, PAGES_REPO)
        elif 'show' == arg:
            sphinx_show(PAGES_DIR)
        elif 'upload' == arg:
            sphinx_upload(PAGES_DIR)
            print()
            print(
                "Do not forget to also commit+push your changes to '_website'")
        else:
            sys.exit('Command "website" does not have subcommand "%s"' % arg)

    def test(self, arg):
        """ Run tests:
                * full - run all tests
                * unit - run tests (also for each backend)
                * any backend name (e.g. pyside, pyqt4, etc.) -
                  run tests for the given backend
                * nobackend - run tests that do not require a backend
                * extra - run extra tests (line endings and style)
                * lineendings - test line ending consistency
                * flake - flake style testing (PEP8 and more)
                * docs - test docstring parameters for correctness
                * examples - run all examples
                * examples [examples paths] - run given examples
        """
        # Note: By default, "python make full" *will* produce coverage data,
        # whereas vispy.test('full') will not. This is because users won't
        # really care about coveraged, but developers will.
        if not arg:
            return self.help('test')
        from vispy import test
        try:
            args = arg.split(' ')
            test(args[0], ' '.join(args[1:]), coverage=True)
        except Exception as err:
            print(err)
            if not isinstance(err, RuntimeError):
                type_, value, tb = sys.exc_info()
                traceback.print_exception(type, value, tb)
            raise SystemExit(1)

    def images(self, arg):
        """ Create images (screenshots). Subcommands:
                * gallery - make screenshots for the gallery
                * test - make screenshots for testing
                * upload - upload the gallery images repository
                * clean - delete existing files
        """

        # Clone repo for images if needed, make up-to-date otherwise
        if not op.isdir(IMAGES_DIR):
            os.chdir(ROOT_DIR)
            sh("git clone %s %s" % (IMAGES_REPO, IMAGES_DIR))
        else:
            print('Updating images repo')
            os.chdir(IMAGES_DIR)
            sh('git pull')

        if not arg:
            return self.help('images')

        # Create subdirs if needed
        for subdir in ['gallery', 'thumbs', 'carousel', 'test']:
            subdir = op.join(IMAGES_DIR, subdir)
            if not op.isdir(subdir):
                os.mkdir(subdir)

        # Go
        if arg == 'gallery':
            self._images_screenshots()
            self._images_thumbnails()
        elif arg == 'test':
            sys.exit('images test command not yet implemented')
        elif arg == 'upload':
            sphinx_upload(IMAGES_DIR)
        elif arg == 'clean':
            self._images_delete()
        else:
            sys.exit('Command "images" does not have subcommand "%s"' % arg)

    def _images_delete(self):
        examples_dir = op.join(ROOT_DIR, 'examples')
        gallery_dir = op.join(IMAGES_DIR, 'gallery')

        # Process all files ...
        print('Deleting existing gallery images')
        n = 0
        tot = 0
        for filename, name in get_example_filenames(examples_dir):
            tot += 1
            name = name.replace('/', '__')  # We use flat names
            imagefilename = op.join(gallery_dir, name + '.png')
            if op.isfile(imagefilename):
                n += 1
                os.remove(imagefilename)
        print('Removed %s of %s possible files' % (n, tot))

    def _images_screenshots(self):
        # Prepare
        import imp
        from vispy.io import imsave
        from vispy.gloo.util import _screenshot
        examples_dir = op.join(ROOT_DIR, 'examples')
        gallery_dir = op.join(IMAGES_DIR, 'gallery')

        # Process all files ...
        for filename, name in get_example_filenames(examples_dir):
            name = name.replace('/', '__')  # We use flat names
            imagefilename = op.join(gallery_dir, name + '.png')

            # Check if we need to take a sceenshot
            if op.isfile(imagefilename):
                print('Skip:   %s screenshot already present.' % name)
                continue

            # Check if should make a screenshot
            frames = []
            lines = open(filename, 'rt').read().splitlines()
            for line in lines[:10]:
                if line.startswith('# vispy:') and 'gallery' in line:
                    # Get what frames to grab
                    frames = line.split('gallery')[1].split(',')[0].strip()
                    frames = frames or '0'
                    frames = [int(i) for i in frames.split(':')]
                    if not frames:
                        frames = [0]
                    if len(frames) > 1:
                        frames = list(range(*frames))
                    break
            else:
                print('Ignore: %s, no hint' % name)
                continue  # gallery hint not found

            # Import module and prepare
            print('Grab:   %s screenshots (%s)' % (name, len(frames)))
            try:
                m = imp.load_source('vispy_example_' + name, filename)
            except Exception as exp:
                print('*Err*:  %s, got "%s"' % (name, str(exp)))
            m.done = False
            m.frame = -1
            m.images = []

            # Create a canvas and grab a screenshot
            def grabscreenshot(event):
                if m.done:
                    return  # Grab only once
                m.frame += 1
                if m.frame in frames:
                    frames.remove(m.frame)
                    im = _screenshot((0, 0, c.size[0], c.size[1]))
                    # Ensure we don't have alpha silliness
                    im = np.array(im)
                    im[:, :, 3] = 255
                    m.images.append(im)
                if not frames:
                    m.done = True
            # Get canvas
            if hasattr(m, 'canvas'):
                c = m.canvas  # scene examples
            elif hasattr(m, 'Canvas'):
                c = m.Canvas()
            elif hasattr(m, 'fig'):
                c = m.fig
            else:
                print('Ignore: %s, no canvas' % name)
                continue
            c.events.draw.connect(grabscreenshot)
            # Show it and draw as many frames as needed
            with c:
                n = 0
                limit = 10000
                while not m.done and n < limit:
                    c.update()
                    c.app.process_events()
                    n += 1
                if n >= limit or len(frames) > 0:
                    raise RuntimeError('Could not collect image for %s' % name)
            # Save
            imsave(imagefilename, m.images[0])  # Alwats show one image
            if len(m.images) > 1:
                import imageio  # multiple gif not properly supported yet
                imageio.mimsave(imagefilename[:-3] + '.gif', m.images)

    def _images_thumbnails(self):
        from vispy.io import imsave, imread
        from skimage.transform import resize
        import numpy as np
        gallery_dir = op.join(IMAGES_DIR, 'gallery')
        thumbs_dir = op.join(IMAGES_DIR, 'thumbs')
        carousel_dir = op.join(IMAGES_DIR, 'carousel')
        for fname in os.listdir(gallery_dir):
            filename1 = op.join(gallery_dir, fname)
            filename2 = op.join(thumbs_dir, fname)
            filename3 = op.join(carousel_dir, fname)
            #
            im = imread(filename1)

            newx = 200
            newy = int(newx * im.shape[0] / im.shape[1])
            im = (resize(im, (newy, newx), 2) * 255).astype(np.uint8)
            imsave(filename2, im)

            newy = 160  # This should match the carousel size!
            newx = int(newy * im.shape[1] / im.shape[0])
            im = (resize(im, (newy, newx), 1) * 255).astype(np.uint8)
            imsave(filename3, im)

            print('Created thumbnail and carousel %s' % fname)

    def copyright(self, arg):
        """ Update all copyright notices to the current year.
        """
        # Initialize
        TEMPLATE = "# Copyright (c) %i, Vispy Development Team."
        CURYEAR = int(time.strftime('%Y'))
        OLDTEXT = TEMPLATE % (CURYEAR - 1)
        NEWTEXT = TEMPLATE % CURYEAR
        # Initialize counts
        count_ok, count_replaced = 0, 0

        # Processing the whole root directory
        for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
            # Check if we should skip this directory
            reldirpath = op.relpath(dirpath, ROOT_DIR)
            if reldirpath[0] in '._' or reldirpath.endswith('__pycache__'):
                continue
            if op.split(reldirpath)[0] in ('build', 'dist'):
                continue
            # Process files
            for fname in filenames:
                if not fname.endswith('.py'):
                    continue
                # Open and check
                filename = op.join(dirpath, fname)
                text = open(filename, 'rt').read()
                if NEWTEXT in text:
                    count_ok += 1
                elif OLDTEXT in text:
                    text = text.replace(OLDTEXT, NEWTEXT)
                    open(filename, 'wt').write(text)
                    print(
                        '  Update copyright year in %s/%s' %
                        (reldirpath, fname))
                    count_replaced += 1
                elif 'copyright' in text[:200].lower():
                    print(
                        '  Unknown copyright mentioned in %s/%s' %
                        (reldirpath, fname))
        # Report
        print('Replaced %i copyright statements' % count_replaced)
        print('Found %i copyright statements up to date' % count_ok)


# Functions used by the maker

if sys.version_info[0] < 3:
    input = raw_input  # noqa


def sh(cmd):
    """Execute command in a subshell, return status code."""
    return subprocess.check_call(cmd, shell=True)


def sh2(cmd):
    """Execute command in a subshell, return stdout.
    Stderr is unbuffered from the subshell."""
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    out = p.communicate()[0]
    retcode = p.returncode
    if retcode:
        raise subprocess.CalledProcessError(retcode, cmd)
    else:
        return out.rstrip().decode('utf-8', 'ignore')


def sphinx_clean(build_dir):
    if op.isdir(build_dir):
        shutil.rmtree(build_dir)
    os.mkdir(build_dir)
    print('Cleared build directory.')


def sphinx_build(src_dir, build_dir):
    import sphinx
    ret = sphinx.main(('sphinx-build',  # Dummy
                       '-b', 'html',
                       '-d', op.join(build_dir, 'doctrees'),
                       src_dir,  # Source
                       op.join(build_dir, 'html'),  # Dest
                       ))
    if ret != 0:
        raise RuntimeError('Sphinx error: %s' % ret)
    print("Build finished. The HTML pages are in %s/html." % build_dir)


def sphinx_show(html_dir):
    index_html = op.join(html_dir, 'index.html')
    if not op.isfile(index_html):
        sys.exit('Cannot show pages, build the html first.')
    import webbrowser
    webbrowser.open_new_tab(index_html)


def sphinx_copy_pages(html_dir, pages_dir, pages_repo):
    # Create the pages repo if needed
    if not op.isdir(pages_dir):
        os.chdir(ROOT_DIR)
        sh("git clone %s %s" % (pages_repo, pages_dir))
    # Ensure that its up to date
    os.chdir(pages_dir)
    sh('git checkout master -q')
    sh('git pull -q')
    os.chdir('..')
    # This is pretty unforgiving: we unconditionally nuke the destination
    # directory, and then copy the html tree in there
    tmp_git_dir = op.join(ROOT_DIR, pages_dir + '_git')
    shutil.move(op.join(pages_dir, '.git'), tmp_git_dir)
    try:
        shutil.rmtree(pages_dir)
        shutil.copytree(html_dir, pages_dir)
        shutil.move(tmp_git_dir, op.join(pages_dir, '.git'))
    finally:
        if op.isdir(tmp_git_dir):
            shutil.rmtree(tmp_git_dir)
    # Copy individual files
    for fname in ['CNAME', 'README.md', 'conf.py', '.nojekyll', 'Makefile']:
        shutil.copyfile(op.join(WEBSITE_DIR, fname),
                        op.join(pages_dir, fname))
    # Messages
    os.chdir(pages_dir)
    sh('git status')
    print()
    print("Website copied to _gh-pages. Above you can see its status:")
    print("  Run 'make.py website show' to view.")
    print("  Run 'make.py website upload' to commit and push.")


def sphinx_upload(repo_dir):
    # Check head
    os.chdir(repo_dir)
    status = sh2('git status | head -1')
    branch = re.match('On branch (.*)$', status).group(1)
    if branch != 'master':
        e = 'On %r, git branch is %r, MUST be "master"' % (repo_dir,
                                                           branch)
        raise RuntimeError(e)
    # Show repo and ask confirmation
    print()
    print('You are about to commit to:')
    sh('git config --get remote.origin.url')
    print()
    print('Most recent 3 commits:')
    sys.stdout.flush()
    sh('git --no-pager log --oneline -n 3')
    ok = input('Are you sure you want to commit and push? (y/[n]): ')
    ok = ok or 'n'
    # If ok, add, commit, push
    if ok.lower() == 'y':
        sh('git add .')
        sh('git commit -am"Update (automated commit)"')
        print()
        sh('git push')


def get_example_filenames(example_dir):
    """ Yield (filename, name) elements for all examples. The examples
    are organized in directories, therefore the name can contain a
    forward slash.
    """
    for (dirpath, dirnames, filenames) in os.walk(example_dir):
        for fname in sorted(filenames):
            if not fname.endswith('.py'):
                continue
            filename = op.join(dirpath, fname)
            name = filename[len(example_dir):].lstrip('/\\')[:-3]
            name = name.replace('\\', '/')
            yield filename, name


if __name__ == '__main__':
    try:
        m = Maker(sys.argv)
    finally:
        os.chdir(START_DIR)
