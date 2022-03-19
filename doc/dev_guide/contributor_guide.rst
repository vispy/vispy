Contributor's Guide
===================

So you're thinking about contributing to VisPy...great! Below you'll find
instructions on the different ways to contribute and how to do it. You'll
also find information about coding style and other best practices.

Who can contribute?
-------------------

VisPy accepts contributions from anyone as long as they meet our standards.
While we will accept contributions from anyone, we especially value ideas and
contributions from folks with diverse backgrounds and identities. There are
many ways to contribute (see below) and no contribution is too small.

What can be contributed?
------------------------

1. **Bugs**: Tell us when you think you've found something wrong or when you
   just can't get something to work after following the instructions.
2. **Features**: Have an idea how VisPy could be improved? We'd like to hear
   it. Bonus points if you have ideas on how it can be implemented.
3. **Ticket Review**: Not sure how to help out, but you've become pretty
   familiar with the project? Help the VisPy maintainers clean out old,
   duplicate, or already resolved bug reports and feature requests.
4. **Documentation**: See a typo? Please correct us. Is something documented
   wrong or out of date? Tell us about it. Could the documentation be made
   less confusing if their was more detail? Let us know. Tell us what was
   confusing. Even better, tell us what would have made it easier to
   understand in the first place. See below for more info on best practices.
5. **Code**: If there is a bug that you want to fix or a feature you want to
   add, please let us know. See below for how we prefer you make these
   contributions.

How can I contribute?
---------------------

Almost all communication with the VisPy maintainers should be done through
the main VisPy GitHub repository: https://github.com/vispy/vispy/

* Bug reports and feature requests can be submitted through the "Issues" on
  the repository.
  `This GitHub page <https://docs.github.com/en/free-pro-team@latest/github/managing-your-work-on-github/creating-an-issue>`_
  can help you create an issue if you're unfamiliar with the process.
  When you create an issue you'll see VisPy's template asking you for
  specific information. It is really important that you provide as much
  of this information as possible. Most importantly for bugs is providing a
  `Minimal Complete and Verifiable Example (MCVE) <https://stackoverflow.com/help/minimal-reproducible-example>`_
* Any changes to actual code, including documentation, should be submitted
  as a pull request on GitHub. GitHub's documentation includes instructions
  on `making a pull request <https://docs.github.com/en/free-pro-team@latest/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request>`_
  if you're new to GitHub or to git in general. Please make sure to submit
  pull requests using a **new** branch (not your fork's main branch).
  Don't be afraid to submit a pull request with only partial fixes/features.
  Pull requests can always be updated after they are created. Creating them
  early gives maintainers a chance to provide an early review of your code if
  that's something you're looking for.
  See below for more information on writing documentation and checking your
  changes.

No matter how you contribute, VisPy maintainers will try their best to read,
research, and respond to your query as soon as possible. For code changes,
automated checks and tests will run on GitHub to provide an initial "review"
of your changes.

What if I need help?
--------------------

The best way to ask for help from VisPy maintainers is to talk to us on
gitter. If you have more general VisPy questions that users may be able to
help with check out the
`main gitter channel <https://gitter.im/vispy/vispy>`_. If you have questions
specific to VisPy's design or how you should contribute to VisPy there is a
gitter channel specifically for
`VisPy Developers <https://gitter.im/vispy/vispy-dev>`_. Lastly, feel free to
create an issue on GitHub to ask a question. If you've already created a
pull request you can comment there.

Development Environment
-----------------------

See the installation instructions for different ways to install VisPy and its
dependencies. We suggest installing VisPy :ref:`from source <dev_install>`
if you are planning on modifying any code.

Coding Style
------------

In general, VisPy follows the PEP 8 style guidelines:

https://www.python.org/dev/peps/pep-0008/

The easiest way to see if your meeting these guidelines is to code as you
normally would and run ``flake8`` to check for errors (see below). Otherwise,
see existing VisPy code for examples of what we expect.

Checking Code Style
^^^^^^^^^^^^^^^^^^^

Code style is automatically checked by VisPy's Continuous Integration (CI).
If you'd like to check the style on your own local machine you can install
and run the ``flake8`` utility from the root of the vispy repository. To
install:

.. code-block:: bash

  pip install flake8

Then run the following from the root of the VisPy directory:

.. code-block:: bash

  python make test flake

This will inform you of any code style issues in the entire vispy python
package directory.

Documentation Style
-------------------

All docstrings in VisPy's python code follow the NumPy style. You can find
the full reference here:

https://numpydoc.readthedocs.io/en/latest/format.html

However, the simplest way to get a hang of this style is to look at the
existing VisPy code.

Checking Documentation Style
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Similar to code style, documentation style is tested during VisPy's automated
testing when you create or edit a pull request. If you'd like to check it
locally you can use the same ``flake8`` tool as for code, but with the
addition of the ``flake8-docstring`` package. To install:

.. code-block::

    pip install flake8-docstrings

Then run the following from the root of the VisPy directory:

.. code-block:: bash

    python make test flake

This will check both code style and docstring style.

Adding Tests
------------

VisPy depends on self-contained tests to know that changes haven't broken any
existing functionality. Our unit tests are written using the ``pytest``
library. Some parts of VisPy require extra steps to test them thoroughly, but
utilities exist to help with this. For example, VisPy has multiple backends
that can be used, so to be thoroughly checked tests should be run for each
of these backends. Luckily, VisPy's automated tests will run every test over
a series of backends for you when you make a pull request so you shouldn't
normally have to worry about this in your local testing.

Writing Tests
^^^^^^^^^^^^^

As mentioned, tests are written so that they can be run with pytest. In the
most basic cases this means adding one or more functions or classes to modules
in a ``tests`` directory. For example, tests for the vispy.plot subpackage are
in the ``vispy/plot/tests/test_plot.py`` module. Note that both the module and
the function should start with ``test_`` so that pytest can discover them.

Tests should completely test the changes being submitted. Depending on the
changes this may be as simple as calling the function or as complicated as
building a full visualization with a Canvas and set of Visual objects. Looking
at existing tests is a good place to start. If you have any questions you can
always contact the VisPy maintainers or leave a comment on your pull request
asking for assistance.

For more complex tests, you may require that certain dependencies be installed
or that a GUI window can be opened. In those case you can look at the various
decorators in :mod:`vispy.testing`. For example, if you need to make a Canvas,
your test should only run when a VisPy Application can be created. In this
case the :func:`~vispy.testing._testing.requires_application` decorator can be
used:

.. code-block:: python

  from vispy.testing import requires_application

  @requires_application()
  def test_my_change():
      with app.Canvas() as c:
          # do something with the Canvas 'c'

All available decorators in the testing module start with ``requires_``. See
the module documentation for more information.

Running Tests
^^^^^^^^^^^^^

In the basic cases, the traditional method of calling ``pytest <module.py>``
will work to run a limited set of tests:

.. code-block::

  pytest vispy/plot/tests/test_plot.py

However, this will only run on one backend. To easily run tests on multiple
backends:

.. code-block::

  python make test unit

This runs tests in the same way that tests are run on the CI environments.
Additional test commands are available including:

.. code-block::

  python make test nobackend

To run tests without any backend selected. Or:

.. code-block::

  python make test full

To run both nobackend and unit tests as well as "extra" tests including
docstring and flake tests. Lastly:

.. code-block::

  python make test examples

Which will attempt to run all example scripts.

.. note::

  Due to environment, GPU driver, or dependency differences not all tests
  may pass on your system. The CI environments should be considered the
  "one truth" for passing tests until tests are made more flexible for
  differences in systems.

Sphinx Documentation
--------------------

VisPy's documentation website is a `Sphinx <https://www.sphinx-doc.org/>`_
project stored in the "doc" directory of the repository. To generate the
documentation run:

.. code-block:: bash

    cd doc
    make html

Repeated execution of ``make html`` will reuse information from previous runs
which may be faster, but may also produce incorrect output in specific cases.
To make sure, you can clean out the build directory by running ``make clean``.

To view the output you can view the build folder in a browser:

.. code-block::

    firefox _build/html/index.html

As part of the documentation generation, the sphinx-gallery project will run
all of the examples to generate screenshots for the gallery pages. This can
take a long time and is unnecessary if you aren't modifying the gallery or
examples. To build the site without generating the gallery run:

.. code-block::

    make html SPHINXOPTS="-D plot_gallery=0"

Jupyter Widget
--------------

VisPy no longer has a jupyter widget as part of the main VisPy Python
package. Instead the "jupyter_rfb" package is used through the "jupyter_rfb"
backend of VisPy. Major changes to this backend will likely need changes to
the jupyter_rfb library which can be found here:

https://github.com/vispy/jupyter_rfb/

Updating my fork's branch to "main"
-----------------------------------

The VisPy project has switched to using the branch name "main" as its primary
branch. If you forked the repository before this change, you may find it
confusing to work between your fork and the upstream VisPy repository.
If you wish to update your fork, go to the branches page for your repository
(ex. ``https://github.com/<yourusername>/vispy/branches``) and edit/rename
the "master" branch to "main".

On your local system, you'll also want to point to the new name as well. GitHub
provides instructions for doing this update. For convenience they've been
copied below:

.. code-block:: bash

    git branch -m master main
    git fetch origin
    git branch -u origin/main main
    git remote set-head origin -a

If you've configured multiple "remotes" on your system, you may need to
change these commands with the proper remote name.
