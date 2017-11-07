# -*- coding: utf-8 -*-
from os import path


def filepath(filename):
    return path.join(path.dirname(path.abspath(__file__)), filename)
