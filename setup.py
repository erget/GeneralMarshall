#!/usr/bin/env python2.7
'''
Created on 22.04.2013

@author: dlee
'''

from distutils.core import setup

from general_marshall import VERSION

setup(name="GeneralMarshall",
      version=VERSION,
      description="An XML marshalling and demartialling library",
      author="Daniel Lee",
      author_email="Daniel.Lee@dwd.de",
      license="GNU GPL",
      url="https://github.com/erget/GeneralMarshall",
      packages=["general_marshall"],
      long_description=open("README").read()
      )
