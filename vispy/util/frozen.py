# -*- coding: utf-8 -*-
# Copyright (c) Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.


# Class adapted from:
# http://stackoverflow.com/questions/3603502/

class Frozen(object):
    __isfrozen = False

    def __setattr__(self, key, value):
        if self.__isfrozen and not hasattr(self, key):
            raise AttributeError('%r is not an attribute of class %s. Call '
                                 '"unfreeze()" to allow addition of new '
                                 'attributes' % (key, self))
        object.__setattr__(self, key, value)

    def freeze(self):
        """Freeze the object so that only existing properties can be set"""
        self.__isfrozen = True

    def unfreeze(self):
        """Unfreeze the object so that additional properties can be added"""
        self.__isfrozen = False
