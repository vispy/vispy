#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for mo

"""
Convenience tools for vispy developers

    make.py command [arg]

"""

from __future__ import division

import sys
import os
import time
import shutil
import subprocess
import re

# Save where we came frome and where this module lives
START_DIR = os.path.abspath(os.getcwd())
THIS_DIR = os.path.abspath(os.path.dirname(__file__))

# Get root directory of the package, by looking for setup.py
for subdir in ['.', '..']:
    ROOT_DIR = os.path.abspath(os.path.join(THIS_DIR, subdir))
    if os.path.isfile(os.path.join(ROOT_DIR, 'setup.py')):
        break
else:
    sys.exit('Cannot find root dir')


# Define directories and repos of interest
DOC_DIR = os.path.join(ROOT_DIR, 'doc')
#
WEBSITE_DIR = os.path.join(ROOT_DIR, '_website')
WEBSITE_REPO = 'git@github.com:vispy/vispy-website'
#
PAGES_DIR = os.path.join(ROOT_DIR, '_gh-pages')
PAGES_REPO = 'git@github.com:vispy/vispy.github.com.git'
#
IMAGES_DIR = os.path.join(ROOT_DIR, '_images')
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
                #doc = getattr(self, command).__doc__.splitlines()[0].strip()
                doc = getattr(self, command).__doc__.strip()
                print(' %s  %s' % (preamble, doc))
            print()

    def doc(self, arg):
        """ Make API documentation. Subcommands:
                * html - build html
                * show - show the docs in your browser
        """
        # Prepare
        build_dir = os.path.join(DOC_DIR, '_build')
        if not arg:
            return self.help('doc')
        # Go
        if 'html' == arg:
            sphinx_clean(build_dir)
            sphinx_build(DOC_DIR, build_dir)
        elif 'show' == arg:
            sphinx_show(os.path.join(build_dir, 'html'))
        else:
            sys.exit('Command "doc" does not have subcommand "%s"' % arg)

    def website(self, arg):
        """ Build website. Website source is put in '_website'. Subcommands:
                * html - build html
                * show - show the website in your browser
                * upload - upload (commit+push) the resulting html to github
        """
        # Prepare
        build_dir = os.path.join(WEBSITE_DIR, '_build')
        html_dir = os.path.join(build_dir, 'html')
        if not arg:
            return self.help('website')

        # Clone repo for website if needed, make up-to-date otherwise
        if not os.path.isdir(WEBSITE_DIR):
            os.chdir(ROOT_DIR)
            sh("git clone %s %s" % (WEBSITE_REPO, WEBSITE_DIR))
        else:
            print('Updating website repo')
            os.chdir(WEBSITE_DIR)
            sh('git pull')

        # Go
        if 'html' == arg:
            sphinx_clean(build_dir)
            sphinx_build(WEBSITE_DIR, build_dir)
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
        """ Run all tests. """
        self.test_nose(arg)
        self.test_flake(arg)

    def test_nose(self, arg):
        """ Run all unit tests using nose. """
        os.chdir(ROOT_DIR)
        sys.argv[1:] = []
        import nose
        nose.run()

    def test_flake(self, arg):
        """ Run flake8 to find style inconsistencies. """
        os.chdir(ROOT_DIR)
        sys.argv[1:] = ['vispy', 'examples', 'make']
        from flake8.main import main
        main()

    def images(self, arg):
        """ Create images (screenshots). Subcommands:
                * gallery - make screenshots for the gallery
                * test - make screenshots for testing
                * upload - upload the images repository
        """
        if not arg:
            return self.help('images')

        # Clone repo for images if needed, make up-to-date otherwise
        if not os.path.isdir(IMAGES_DIR):
            os.chdir(ROOT_DIR)
            sh("git clone %s %s" % (IMAGES_REPO, IMAGES_DIR))
        else:
            print('Updating images repo')
            os.chdir(IMAGES_DIR)
            sh('git pull')

        # Create subdirs if needed
        for subdir in ['gallery', 'thumbs', 'test']:
            subdir = os.path.join(IMAGES_DIR, subdir)
            if not os.path.isdir(subdir):
                os.mkdir(subdir)

        # Go
        if arg == 'gallery':
            self._images_screenshots()
            self._images_thumbnails()
        elif arg == 'test':
            sys.exit('images test command not yet implemented')
        elif arg == 'upload':
            sphinx_upload(IMAGES_DIR)
        else:
            sys.exit('Command "website" does not have subcommand "%s"' % arg)

    def _images_screenshots(self):
        # Prepare
        import imp
        from vispy.util.dataio import imsave
        from vispy.gloo import _screenshot
        examples_dir = os.path.join(ROOT_DIR, 'examples')
        gallery_dir = os.path.join(IMAGES_DIR, 'gallery')

        # Process all files ...
        for filename, name in get_example_filenames(examples_dir):
            name = name.replace('/', '__')  # We use flat names
            imagefilename = os.path.join(gallery_dir, name + '.png')

            # Check if should make a screenshot
            frames = []
            lines = open(filename, 'rt').read().splitlines()
            for line in lines[:10]:
                if line.startswith('# vispy:') and 'gallery' in line:
                    # Get what frames to grab
                    frames = line.split('gallery')[1].strip()
                    frames = frames or '0'
                    frames = [int(i) for i in frames.split(':')]
                    if not frames:
                        frames = [0]
                    if len(frames) > 1:
                        frames = list(range(*frames))
                    break
            else:
                continue  # gallery hint not found

            # Check if we need to take a sceenshot
            if os.path.isfile(imagefilename):
                print('Screenshot for %s already present (skip).' % name)
                continue

            # Import module and prepare
            m = imp.load_source('vispy_example_' + name, filename)
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
                    print('Grabbing a screenshot for %s' % name)
                    im = _screenshot((0, 0, c.size[0], c.size[1]))
                    m.images.append(im)
                if not frames:
                    m.done = True
            c = m.Canvas()
            c.events.paint.connect(grabscreenshot)
            c.show()
            while not m.done:
                m.app.process_events()
            c.close()

            # Save
            imsave(imagefilename, m.images[0])  # Alwats show one image
            if len(m.images) > 1:
                import imageio  # multiple gif not properly supported yet
                imageio.mimsave(imagefilename[:-3] + '.gif', m.images)

    def _images_thumbnails(self):
        from vispy.util.dataio import imsave, imread
        from skimage.transform import resize
        import numpy as np
        gallery_dir = os.path.join(IMAGES_DIR, 'gallery')
        thumbs_dir = os.path.join(IMAGES_DIR, 'thumbs')
        for fname in os.listdir(gallery_dir):
            filename1 = os.path.join(gallery_dir, fname)
            filename2 = os.path.join(thumbs_dir, fname)
            #
            im = imread(filename1)
            newx = 200
            newy = int(newx * im.shape[0] / im.shape[1])
            im = (resize(im, (newy, newx), 2) * 255).astype(np.uint8)
            imsave(filename2, im)
            print('Created thumbnail %s' % fname)

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
            reldirpath = os.path.relpath(dirpath, ROOT_DIR)
            if reldirpath[0] in '._' or reldirpath.endswith('__pycache__'):
                continue
            if os.path.split(reldirpath)[0] in ('build', 'dist'):
                continue
            # Process files
            for fname in filenames:
                if not fname.endswith('.py'):
                    continue
                # Open and check
                filename = os.path.join(dirpath, fname)
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
    if os.path.isdir(build_dir):
        shutil.rmtree(build_dir)
    os.mkdir(build_dir)
    print('Cleared build directory.')


def sphinx_build(src_dir, build_dir):
    import sphinx
    sphinx.main(('sphinx-build',  # Dummy
                 '-b', 'html',
                 '-d', os.path.join(build_dir, 'doctrees'),
                 src_dir,  # Source
                 os.path.join(build_dir, 'html'),  # Dest
                 ))
    print("Build finished. The HTML pages are in %s/html." % build_dir)


def sphinx_show(html_dir):
    index_html = os.path.join(html_dir, 'index.html')
    if not os.path.isfile(index_html):
        sys.exit('Cannot show pages, build the html first.')
    import webbrowser
    webbrowser.open_new_tab(index_html)


def sphinx_copy_pages(html_dir, pages_dir, pages_repo):
    # Create the pages repo if needed
    if not os.path.isdir(pages_dir):
        os.chdir(ROOT_DIR)
        sh("git clone %s %s" % (pages_repo, pages_dir))
    # Ensure that its up to date
    os.chdir(pages_dir)
    sh('git checkout master -q')
    sh('git pull -q')
    # This is pretty unforgiving: we unconditionally nuke the destination
    # directory, and then copy the html tree in there
    tmp_git_dir = os.path.join(ROOT_DIR, pages_dir + '_git')
    shutil.move(os.path.join(pages_dir, '.git'), tmp_git_dir)
    try:
        shutil.rmtree(pages_dir)
        shutil.copytree(html_dir, pages_dir)
        shutil.move(tmp_git_dir, os.path.join(pages_dir, '.git'))
    finally:
        if os.path.isdir(tmp_git_dir):
            shutil.rmtree(tmp_git_dir)
    # Copy individual files
    for fname in ['CNAME', 'README.md', 'conf.py', '.nojekyll', 'Makefile']:
        shutil.copyfile(os.path.join(WEBSITE_DIR, fname),
                        os.path.join(pages_dir, fname))
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
    branch = re.match('\# On branch (.*)$', status).group(1)
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
        for fname in filenames:
            if not fname.endswith('.py'):
                continue
            filename = os.path.join(dirpath, fname)
            name = filename[len(example_dir):].lstrip('/\\')[:-3]
            name = name.replace('\\', '/')
            yield filename, name


if __name__ == '__main__':
    try:
        Maker(sys.argv)
        # Maker(('bla', 'gallery'))
    finally:
        os.chdir(START_DIR)
