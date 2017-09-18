# -*- coding: utf-8 -*-
from os import path


def open(filename, *args, **kwargs):
    filepath = path.join(path.dirname(path.abspath(__file__)),
                         filename)
    return open(filepath, *args, **kwargs)
