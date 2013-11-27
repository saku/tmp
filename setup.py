#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
import sys

if not (2, 7) <= sys.version_info[:2] :
    raise Exception("sample server requires a Python 2 version newer than 2.7. \nYour python version is %s." % sys.version)

from distutils.core import setup

setup(
      name = "sampleServer",
      version = "0.1",
      author = "Yoichiro Sakurai",
      description = "Sample server with test.",
      author_email = "saku2saku@retty.me",
      url = "http://retty.me/",
      packages=['python'],
      package_data={'python': ['*.html']},
     )
