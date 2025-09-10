#! /usr/bin/env python3
# -*- coding: utf-8 -*-
""" re patterns """
from __future__ import annotations

from re import DOTALL, MULTILINE, Pattern, compile

answer_re: Pattern[str] = compile(r'Answer: .*')
docstring_re: Pattern[str] = compile(r'(""".*?""")', DOTALL | MULTILINE)
stubber_re: Pattern[str] = compile(r'(def\s.*?:)\n(.*?)\n\n\n', DOTALL | MULTILINE)
summary_re: Pattern[str] = compile(r'^## Summary Dashboard.*', MULTILINE | DOTALL)

__all__ = ['answer_re', 'docstring_re', 'stubber_re', 'summary_re']
