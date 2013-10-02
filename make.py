#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for mo

"""
Convenience tools for vispy developers

    make.py target [arg]

"""

from __future__ import print_function, division

import sys
import os
import shutil
import subprocess
import re


START_DIR = os.path.abspath(os.getcwd())
THIS_DIR = os.path.abspath(os.path.dirname(__file__))
DOC_DIR = os.path.join(THIS_DIR, 'doc')
WEBSITE_DIR = os.path.join(THIS_DIR, '_website')
WEBSITE_REPO = 'git@github.com:vispy/vispy-website'
PAGES_DIR =  os.path.join(THIS_DIR, '_gh-pages')
PAGES_REPO = 'git@github.com:vispy/vispy.github.com.git'



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
            print(__doc__.strip()+ '\n\nCommands:\n')
            for command in sorted(dir(self)):
                if command.startswith('_'):
                    continue
                preamble = command.ljust(10)
                doc = getattr(self, command).__doc__.splitlines()[0].strip()
                print(' %s  %s' % (preamble, doc))
            print()
    
    
    def doc(self, arg):
        """ Build API documentation. 
        Accepted arguments: 
          * clean - clean the build directory
          * html - build html
          * show - show the docs in your browser
        Multiple arguments can be given, e.g. 'make.py doc clean html'.
        By default the argument is 'clean html'.
        """
        # Prepare
        build_dir = os.path.join(DOC_DIR, '_build')
        if not arg:
            arg = 'clean html'
        # Go
        if 'clean' in arg:
            sphinx_clean(build_dir)
        if 'html' in arg:
            sphinx_build(DOC_DIR, build_dir)
        if 'show' in arg:
            sphinx_show(os.path.join(build_dir, 'html'))
    
    
    def website(self, arg):
        """ Build website. Website source is put in '_website'. 
        Accepted arguments: 
          * clean - clean the build directory
          * html - build html
          * show - show the website in your browser
          * upload - upload (commit+push) the resulting html to github pages.
        Multiple arguments can be given, e.g. 'make.py website clean html'.
        By default the argument is 'clean html'.
        Note that the the website source is not automatically commited.
        """
        # Prepare
        build_dir = os.path.join(WEBSITE_DIR, '_build')
        html_dir = os.path.join(build_dir, 'html')
        if not arg:
            arg = 'clean html'
        
        # Clone repo for website if needed
        if not os.path.isdir(WEBSITE_DIR):
            os.chdir(THIS_DIR)
            sh("git clone %s %s" % (WEBSITE_REPO, WEBSITE_DIR))
        
        # Always pull to get latest version
        os.chdir(WEBSITE_DIR)
        sh('git pull')
        
        # Go
        if 'clean' in arg:
            sphinx_clean(build_dir)
        if 'html' in arg:
            sphinx_build(WEBSITE_DIR, build_dir)
            sphinx_copy_pages(html_dir, PAGES_DIR, PAGES_REPO)
            for fname in ['CNAME', 'README.md', 'conf.py', '.nojekyll', 'Makefile']:
                shutil.copyfile(os.path.join(WEBSITE_DIR, fname), 
                                os.path.join(PAGES_DIR, fname))
            print("Do not forget to commit and push your changes to '_website'")
        if 'show' in arg:
            sphinx_show(PAGES_DIR)
        if 'upload' in arg:
            sphinx_upload(PAGES_DIR)
    


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
    sphinx.main((   'sphinx-build',  # Dummy 
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
        os.chdir(THIS_DIR)
        sh("git clone %s %s" % (pages_repo, pages_dir))
    # Ensure that its up to date
    os.chdir(pages_dir)
    sh('git checkout master -q')
    sh('git pull -q')
    # This is pretty unforgiving: we unconditionally nuke the destination
    # directory, and then copy the html tree in there
    tmp_git_dir = os.path.join(THIS_DIR, pages_dir+'_git')
    shutil.move(os.path.join(pages_dir, '.git'), tmp_git_dir)
    try:
        shutil.rmtree(pages_dir)
        shutil.copytree(html_dir, pages_dir)
        shutil.move(tmp_git_dir, os.path.join(pages_dir, '.git'))
    finally:
        if os.path.isdir(tmp_git_dir):
            shutil.rmtree(tmp_git_dir)
    # Messages
    os.chdir(pages_dir)
    sh('git status')
    print()
    print("Website copied to _gh-pages. Above you can see its status:")
    print("  Run 'make.py website show' to view.")
    print("  Run 'make.py website upload' to commit and push.")


def sphinx_upload(pages_dir):
    # Check head
    os.chdir(pages_dir)
    status = sh2('git status | head -1')
    branch = re.match('\# On branch (.*)$', status).group(1)
    if branch != 'master':
        e = 'On %r, git branch is %r, MUST be "master"' % (pages_dir,
                                                            branch)
        raise RuntimeError(e)
    sh('git add .')
    sh('git commit -am"Updated website (automated commit)"')
    print()
    print('Most recent 3 commits:')
    sys.stdout.flush()
    sh('git --no-pager log --oneline -n 3')
    sh('git push')



if __name__ == '__main__':
    try:
        Maker(sys.argv)
    finally:
        os.chdir(START_DIR)
