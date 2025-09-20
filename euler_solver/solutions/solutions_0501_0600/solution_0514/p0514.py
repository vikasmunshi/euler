#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 514: Geoboard Shapes.

Problem Statement:
    A geoboard (of order N) is a square board with equally-spaced pins
    protruding from the surface, representing an integer point lattice
    for coordinates 0 <= x, y <= N.

    John begins with a pinless geoboard. Each position on the board is a
    hole that can be filled with a pin. John decides to generate a random
    integer between 1 and N+1 (inclusive) for each hole in the geoboard.
    If the random integer is equal to 1 for a given hole, then a pin is
    placed in that hole.

    After John is finished generating numbers for all (N+1)^2 holes and
    placing any/all corresponding pins, he wraps a tight rubberband
    around the entire group of pins protruding from the board. Let S
    represent the shape that is formed. S can also be defined as the
    smallest convex shape that contains all the pins.

    The above image depicts a sample layout for N = 4. The green markers
    indicate positions where pins have been placed, and the blue lines
    collectively represent the rubberband. For this particular
    arrangement, S has an area of 6. If there are fewer than three pins
    on the board (or if all pins are collinear), S can be assumed to have
    zero area.

    Let E(N) be the expected area of S given a geoboard of order N. For
    example, E(1) = 0.18750, E(2) = 0.94335, and E(10) = 55.03013 when
    rounded to five decimal places each.

    Calculate E(100) rounded to five decimal places.

URL: https://projecteuler.net/problem=514
"""
from typing import Any

euler_problem: int = 514
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 1}, 'answer': None},
    {'category': 'main', 'input': {'n': 100}, 'answer': None},
]
encrypted: str = (
    'u26Gt1m9mwlYeQZX/UaII0saTfsuNmFcgbkxLouH7cGwMw4RZ3IYBn5xSll5oQ3mMlEUtK9D8Yu4cIIX'
    'czdnJhbYQYPe3NvxL7D4ScDIR9f5QiVmbVy8hvwaVhv2VJWpVb02faAz9VJlzXBf+w39oltV72vAhtCA'
    '0rYLMpGWHKdlBKQId3s0NZf+Sw1DgknuXZVbPHpoxz1arcGKRPRQdMhcvONL+ZVCvR8FiOBrUF+Ro2pV'
    'b5ihwBfq1RIUpbBXMPRmPtMhCqLTYaoKTsJKQx5ivOAz0XLBlqVjVKo8eY1cLG740WELWdqg7ck0t6dQ'
    '+q5VejOCINGT+deto2BgGJhDmwxEwKXosp7zvTigQ2kKYLS5JDZO28kSD5piKB1GarhnzIk20R5QMmf0'
    'CocuOT8OQTVgUin6PxKRrCcVizWWV6yGyAtJ7WUV0wQUoUGCHKHbJ9GgeIWiQptE+xaZyUvDv3EEjJxF'
    '40EJGbqQ8wF2vfjfmQ6nkPweJady+g63Nv1bdtMGncS37rPTnDabe1iUjxD05v/nto+yQV0AbJHyJ8ws'
    'WJmK9poxKn4Y/nEfoLYYolZf1XzaUmGUaWpCNO0BpK3gFxCZKiIVimOW/MpbkLgm8Xq5rC9lLqoJYMDV'
    'uwGz7IKmVxvbvbHooDkuDrMCTPFX1lp4Sr0F5GhEsWj/cuqTyNUbkkJlefcOzLrngsEimX0fyK5Ej9Kf'
    'bEqDweQyHULxKlTkWTiQlHqLXMuSbpV0GNeRf4darcqvebIbZ2ayg/oT2b0Q1u0hU/oBKutTkt1EN6DJ'
    '4Nlht4c5AwKMm7kiD0VtEVfyQ97l15IupeUgqaI5Mdhni2Mp+EfLdIY1y5SgMbB/JSnvfPA01RtdmXQv'
    'bpiT8Kwi4yKmOpsZifGarjQnIEYVgefbJndyUyxHwH/WwP3fclARQVtodpkL76jspqcGjVLUpbX5H7eM'
    'RwWqLrYA69CvtzDD3v40oDXL1hUkUutNn+AYF1IADajXPSkQxpYhpMMKWLFg6+Jjf+jEj4obBXWGfyTA'
    'TiYfKOR7PT0W6Ai5k78Xr9RUAm4M0ilBPLce2PH5uMh80ZxenNA2nQQP/9z1ozEV3/7l16JXae0juXrW'
    'ZjvwvJevBIs/G078g1bBV9CnYan3v7H2Bk/jYEwT/f4vB8Q5+Vev4f7fYzk3XHSojLHrajaymn+sj3L3'
    'JdQATJoyBMQkbqvbBN/Z56fDJeF0ZsTzUMoWH1m//FqCpVawx2VkfaZ+iUuvXYJ6ri/R4EWD8cCxohjV'
    'l2FzY+oxro6avVO+qqcU4kh+ts4M4qSjFTyw0e4kSIpoYhwM8QO0bj5TBitFphB68Uiwe1KPfr8HxYQJ'
    'KsG6saOyfz6YRNJ96gt7yHFkBbfbmqS6I90gcDZ/Mc1dyRGplVuDWv3eHcCL4i7MyjuMdLluTzh77QFN'
    'aWbHXWDi0xsm8MnjRj4q6J/XkZ6HBMW/tzwgVr2uFK6wi0NY0tifyzirYlduNHjP8gITWVFOIym48pG5'
    'j18xGBLZv0M4sxQCMaoODZizUftfjDJ4vkPO9/3g2/WMB4xZf02lxPpw8Lh38MgtbtICzxXAlBW/0goa'
    'QeLcXA6StQfwbN4z6psyXQQxoEEtD3iyDroeatkwZrHClgBzQOb29JJYpqu8j/jfk3p14rqxzwjq/JhJ'
    'IRysjNnqq9fr364Ka/bk2pFVaO3bJMy5CO4+OyhHFWnscUpccwo3gUj9YF5CkkQcv5dzy5DnGWtCOUba'
    'mF9f155L3P01XDgQhvsl9LkeZCXyY+M0hZoVlBeDrCMuOByesajID/2eO3bdXZQfuA7ZxjCQn2RQsavn'
    'Sqf9esh6NbExbmjwrgHjOGHd3VtIxgSBzX7K9k4ZPw2KvcT9BqeKNyr6LWAKQK/3oqKk/adGeKiroqVL'
    'hOzwnm32jqkSNNaQXlRQ6c/Wv65U84tT41xZBR+LoTL2t6aqVQ/m6xJhSCUdKuFeZj/8T0cpe7kcah75'
    'W02FrBFO5iyXPXlyqOUlomjk4bLM7J45zwiTbjvPZxfbxARSfArRq9BYG/Au67OGge5AAqmgY6RJOsjr'
    'OmK2c6oU/e8u/vw1Kh4XEpMcLP9JfasgPT6Y9ok1jB4WpFHx/gCYilyafryKpv2Rrdk5EfUFK22xAmoT'
    'aiZlbD0kqwloiLRCKnVOct5S1whY2LBPKLEkFWmcFUKdu1lrk23X+PY6ODj2SpaWZoI5AXkCmZOBnp4z'
    'pFkAHnnA2y5rxXAztuVkY3oPEz3qm57OlC0QhftuU+7ac62EGt1u6QPLCIR7xunRsPf7iUWjJ9f6pQsY'
    'bm3ONUlhU2Kfvpwx3vNyZUq5T32X8weAVl/PGvmesbqvBkaEYwQsN8CMU7ynTpHyzAn7gp0zyqeHYr1/'
    'qrB3GV/VgDw+y7fHi4tOMEBSjLalyMlSctdJOP4FJh/hT2ZIcwsmXqtTpvoHKBbF/hgCJD/x+heZFqNh'
    'f4TbOzCTnuTqKLAsodWMsQfWOfcM0/g2pklXcss621kpKDDUeLFP1YLBUimGJcTz6gfIZqTuaSVZxwGt'
    'uHVz887Y9EsSZ++nPQRnAtQC+yJQYsvHBi+R5YLmf/ggTSD/VpYwuHd+MsIPgSckjbWNA9TtEoJJ1nnG'
    '56hJ8HmHjc9i5dPR9fqzqr9jLYaLcwrj3meet2rGKIlBzTWHokPYxR8GvXQFELsL5HTfbAOYMU5zYLyl'
    'gcOeLs58hhl73ayRlmGI/vtip4kfCzAqRiYirB/Zx70bR92xeJ61+/R9afqKH8KDjxq7q1NG6Iouhf0O'
    '7YJtiMQ5uPpA4ytahTZSDhn5xOctx1GwMMyAM6lITdNLm+wH0KsX/DgTAfDAj8mxH7TUtMaXuRKDGdlp'
    'oqGJu72qdKon2SrO6MaPZ8picK3+Ddyl/l80NvZSKm0sRRjM4DpXlFXtiLVkayU3B70uBxkF/YODTKYM'
    '4KkqK+QTD8PPMC8uhZyUqvGpSzS5wuTYrvyNSCDH5DWoaaQMD2W3EfFV8aWh2OP7XPy0IGZMPlsOnWCS'
    'GA9NBfvrDvgW2BDoY+GDk61I0+HzLaWR/Ix9BkGmNf/NlTMmEoWH15KRgzEK44GmtUKANkRsSbMdHz84'
    'sz6vpRmshuWWXWa7PJ9m8VKaGWLV+BQhwYJYNFPfDrNk7PXcT0Oq3bKkYJYP6eNlsZYfgPxRON0PsccF'
    'GVbOmcmWJEf3ngJguqH8Odl1KMkNB8n9QpRta5RfQXYP00OjYChULC23t14l88ciGbFmgQBDnjonRzhg'
    'Kx6cyem3g33wxGDbrz7o7dpVfGb7N7MZ7zCUlIEQZBwnP29iWcxQKauwHnBYrhot3+du1foFTevbKp+o'
    'D2WT1ErAZCarC97PH4cTQbSoPPicDyMB+8+QSIXBJJPSJHS8aQzNB3zXZX71vQvqkP9nNOQFF0HwA7aR'
    'hadDIchz4fIj2ZQS8Lah/DRQqdkxsC/PEZkn5ZU5QC0IY4Ugm+kQswlt/ZwjacZAkjGF1/GiLqYMEelj'
    'Qe6rsxyGF5lBusWcZkJjG30yIlXNgFfnO8fvISJ1hApeHVgT0B34DTjwq5KuyiNU86QCNdWj6QOHuhvr'
    'EHUz7I2GlXXggi14gKKz3ygHneAF02VtXJxHGeR1iJdh4K2uW4SBmwqqvsYJQzCjRn+bp9aHMIBtEv4E'
    '0ZaXplB8kW1WZGx8pxgNdTyhG0ikIFcRFwktjVcXpawhGTpG9+YDhqacG5tZ53rjN0G6eHi+hsD40JfE'
    'QUmd8sY2SdKbN+TyqtgWdoEn3ZEGoTNJ2WDv5lgOYuq6eRM3+cXd/liwk3yPcB3j1EIKWaC44EAJBXqX'
    'O2sRIX2DnHz7qRG39frQPXLLAds6jWkVRE8fstGPRAy6oRK6LH+yvrpZRbWPyBYbZV7SQpsvBK37gndJ'
    'h1XKgP3GJbY5EwXckND14yBSMRI='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
