#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from Cython.Build import cythonize
from setuptools import Extension, setup

setup(
        ext_modules=cythonize([
            Extension('integer_partitions', sources=['integer_partitions.pyx']),
            Extension('is_prime', sources=['is_prime.pyx']),
            Extension('sum_digits', sources=['sum_digits.pyx']),
        ]),
        script_args=['build_ext', '--inplace'],
)
