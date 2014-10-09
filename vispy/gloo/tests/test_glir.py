# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy development team. All rights reserved.
# Distributed under the terms of the new BSD License.
# -----------------------------------------------------------------------------

from vispy.gloo import glir

from vispy.testing import run_tests_if_main

# todo: implement a few GLIR tests


def test_glir():
    q = glir.GlirQueue()
    q.command('FOO', 0)


run_tests_if_main()
