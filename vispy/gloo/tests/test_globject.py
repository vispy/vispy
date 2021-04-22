# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All rights reserved.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------

from vispy.testing import run_tests_if_main
from vispy.gloo.globject import GLObject


def test_globject():
    """Test gl object uinique id and GLIR CREATE command"""
    objects = [GLObject() for i in range(10)]
    ids = [ob.id for ob in objects]

    # Verify that each id is unique (test should not care how)
    assert len(set(ids)) == len(objects)

    # Verify that glir commands have been created
    commands = []
    for ob in objects:
        commands.extend(ob._glir.clear())
    assert len(commands) == len(objects)
    for cmd in commands:
        assert cmd[0] == 'CREATE'

    # Delete
    ob = objects[-1]
    q = ob._glir  # get it now, because its gone after we delete it
    ob.delete()
    cmd = q.clear()[-1]
    assert cmd[0] == 'DELETE'


run_tests_if_main()
