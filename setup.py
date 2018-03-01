#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='itunes_last_export',
      version='0.1',
      description='Tool to import playcounts and loved tracks from your last.fm account into iTunes',
      author='Vincent Verdeil',
      author_email='vincent.verdeil@gmail.com',
      url='https://github.com/werdeil/itunes-last-export',
      scripts=['bin/itunes_last_export'],
      packages=['itunes_last_export'],
      package_data={'itunes_last_export': ['*.png']},
      )
