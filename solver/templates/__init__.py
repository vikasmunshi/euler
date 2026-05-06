#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path
from string import Template

html_template: Template = Template((Path(__file__).parent.joinpath('template.html')).read_text())

__all__ = ('html_template',)
