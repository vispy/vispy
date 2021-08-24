# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
ptime.py -  Precision time function made os-independent
"""

import time as systime
# get a reference starting time - initial performance counter
START_TIME = systime.time() - systime.perf_counter()


def time():
    # return reference starting time + delta of performance counters
    return START_TIME + systime.perf_counter()
