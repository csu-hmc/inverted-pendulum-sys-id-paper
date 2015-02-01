#!/usr/bin/env python

from distutils.core import setup
from distutils.extension import Extension

from Cython.Build import cythonize
import numpy

extension = Extension(name="fast_interpolate",
                      sources=["fast_interpolate.pyx"],
                      include_dirs=[numpy.get_include()])

setup(name="fast_interpolate",
      ext_modules=cythonize([extension]))\
