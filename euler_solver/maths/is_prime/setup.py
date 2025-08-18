#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from Cython.Build import cythonize
from setuptools import Extension, setup

setup(
        ext_modules=cythonize(Extension(
                "is_prime_cython",
                sources=["is_prime_cython.pyx"],
        )),
        script_args=["build_ext", "--inplace"],
)
