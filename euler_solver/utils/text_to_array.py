#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Text to Array"""
from __future__ import annotations

from typing import List


def text2triangle(text: str) -> List[List[int]]:
    return [[int(num) for num in line.split(' ')] for line in text.splitlines() if line != '']
