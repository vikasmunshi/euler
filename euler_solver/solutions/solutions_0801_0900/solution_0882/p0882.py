#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 882: Removing Bits.

Problem Statement:
    Dr. One and Dr. Zero are playing the following partisan game.
    The game begins with one 1, two 2's, three 3's, ..., n n's.
    Starting with Dr. One, they make moves in turn.
    Dr. One chooses a number and changes it by removing a 1 from its binary expansion.
    Dr. Zero chooses a number and changes it by removing a 0 from its binary expansion.
    The player that is unable to move loses.
    Note that leading zeros are not allowed in any binary expansion; in particular nobody
    can make a move on the number 0.

    They soon realize that Dr. Zero can never win the game. In order to make it more
    interesting, Dr. Zero is allowed to "skip the turn" several times, i.e. passing the
    turn back to Dr. One without making a move.

    For example, when n = 2, Dr. Zero can win the game if allowed to skip 2 turns.
    A sample game:
    [1, 2, 2] -> Dr. One -> [1, 0, 2] -> Dr. Zero -> [1, 0, 1] -> Dr. One -> [1, 0, 0]
    -> skip by Dr. Zero -> [1, 0, 0] -> Dr. One -> [0, 0, 0] -> skip by Dr. Zero -> [0, 0, 0].

    Let S(n) be the minimal number of skips needed so that Dr. Zero has a winning strategy.
    For example, S(2) = 2, S(5) = 17, S(10) = 64.

    Find S(10^5).

URL: https://projecteuler.net/problem=882
"""
from typing import Any

euler_problem: int = 882
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2}, 'answer': None},
    {'category': 'dev', 'input': {'n': 5}, 'answer': None},
    {'category': 'main', 'input': {'n': 100000}, 'answer': None},
]
encrypted: str = (
    'Wuu6QO3kU1byVc+gVtOHOy1CgT+Up1KA04lkcnsAYyGO7WROOj+O/6p4rrlGgaeX+XpbyP9bDZxzqAWQ'
    'XkEtzS4fkoOfit+FWQfIorxZwkKwMWJ3pj8unKTVU/Vmzcm7+0EtUazZdtk/jU46B9DZJBVKp6gCAO3S'
    'mcWY2zR/Y3l94EkVxXk5biFFnA+ybpV/kr3Y+BpeyaRNST7+NlF2g6abPAH2KZ4epArdF8UGB/3zuQKc'
    'ym8mQ3diLJh1wKqYFtddI2Qd3RA3xByNqg5GKpiHBm1Tcmws6Ocm+59U9uzVU8Or6aph3nmub90CdxcS'
    'VzYJYDkJebGbVHnEKAX7VQycRbMFWZSVXfvQa1549Dz+YUqwrUvg/4IXtZ5YFhDMCbw8Osx7LPXurKEa'
    'd9KMqzZvSqhgDqjw7CnULHh4PkFWLnvsdyELTYBQVBtQE7Eg154mUyRsL7SPIu8C7ONnlIXz5B74nwXe'
    'GPDdZFSoMi72CfprTxH2R6lGdyis+xr8WRuatC608EDTVRXJ6zCLAGL695jMF4Ub5JC2E//0h11DKYiu'
    'vW8qCy1LduQnhRzFBEtBIk4GVVOqHcZmOwECe+igDnz9eXpepQCk+emWUx+2073Tt0+98Kl4TvK9Dzvm'
    'G4mAnG/RiqUOgmvIrTH314+Te4GmaHjX92Vgx6dq856UcXnOzGO7Gs3FvqALoMu55DWEdb7uRPm/Gorn'
    'wHOnl14oDU/ELYqm433Hbi+U/JPh+EJgr3wCTgvL6Qx4kY7XZTrgezgaZdnM+l+06j6PpMTBCdvreaZ8'
    'YHxeA2L/dbZj1nJhpNct2vfU4Q681iVApATa0MEWM4CFx6xrwtHRmIPyFjEwtzsd0XF6vabq6ZukmHaa'
    'i1MyMYvYylTCXLpgMmesh7GTgcFp/kjeCWocZZNz+d8I3V4IFxqwTobWQCcDJJtdhn6RtLtejqNOyFC6'
    'Gck0MQHtiH0e7O39CSrhSmq5g1/J4w6sHUmx1je8fl6D3VHkbATM/KmMh4Gouh/yVZMvqE22AJMwjPlS'
    'R9zBXj6yN6IxHN0kgve6VHAo6dJB2di0mL063gP8iNhrZUQst/CkSrMvLs5hILBA7wjfJ6fwFjIXgvbl'
    'FHZoK2KxRSLbgnzzQuU2QZvjgoVraUuNH0HCuUq9Ai8SZRr5nTwDrFFFTj/Kg7BbhYu4+yUx7Fhqci0Q'
    'JzGVkAilsJf8QS5y1C7uWFSYuvWGVwbAae0MfK4QTBvKNne0sVbBUJunjrEU+ZJ0nmFc/i4WJdvM8JXV'
    'tASMI0VS10znFel6c/fRUYZ775YXFqprDn0zcoWGT/b4pzArt+HinfiF2rZzZT01g88WQIcIZF1INyl5'
    'ZG3W/eCjEhOL8HNtn/Fh+VjhSs5uheYx1vbi3I7BrDnrv/bdkcS1Zj0yhzDUyjeqzih+4j1QnWr3ZK0n'
    'E2Uz4/ksZhLxd1JBQ/3wC7d0+kGk0BM7HRH4yLv+2BBoDCfNzs0bU5oUPDumJUAjYUCcn/kYQlTNNN0W'
    'y0zIR+zggp4ilACOqeh1Pf6gsxC5rB6N+uKApjcj/WmIuKPXYVSDbznb3DJvJ/8y4miI7pdgNHceNJGM'
    'g/OWynaypklNCg5BgLybg3U1HS1ZhukuvUmpmfeu2R1YxidXGwP1ZPHbIALI5xrnuPukwBUZcdFPXR2Q'
    'GUsE8hiszaZU+4Jubvvix5J4KvGVL+V4cr84mvunNB7/9ngMp8pc2iN7W3s3S49A8CmiSSRyg/lXZ8Yb'
    'sZKQJAvBgQdglzm76TY7e3n2eZsJtvSZCxJnP89bmDx8DTK+OYWxYpMEs1JbCdr7WnVLHsP2qEBXOV6E'
    'OUUnK1fgRlz+aqzOtZqYh49A5MnChugcvNMD/9l2rEaMR1esUqqV541k334YpMoZiX6huvmngGTaJ0mw'
    'zzQaAeA6vqZmOnIR2CyJxSuXk6uBQz0aw90mc2YKoozPA0qTyMJzQQrz05cfRFVenugsFru/bh4GSpcj'
    'Ezr/MI2Enb5yqm/EnthTOBKO0TmFFbKIHWS/An4OHNyDn978nfRSpbvZa6ZN1i2x1sxJeBY+sB0y8BqU'
    'MpvEUOyL1ETfytsvvefrHlRvKzy8ZGz1ATlBePYcnIZlP1uEmk1+0otc0+aOzDofOYmdVAz+TuksBQc3'
    'Cjd+l0OdocH/mJpJ0DAhvo2A3aKBEzfWJ45SkUyhRIEIkTPN8IuUd5mddnUjK+csp3E0Zg5kBAD8U35K'
    'YwmaO1+mfQtaBHVGYNU7gXBKbYGiBvjK+EHQIN6mbMN0DQpNUFzrCbmFvZTm77NrwcKz0XP+dxIEyR1L'
    'WiJ6/1twdW3xcshcS0+xrLuiZBKU0yT+5T+ZNaCtLdVEsuTRPUa8D2BgicZL6GEtX+1DYEXBkARNZEAC'
    'iOisEWFpi+Y3RZtpcfE8FWqtX0RZ2F7avNXrMY0kFHsAhZsC0CmM4kKtBDZd3qBxqNZCcylQE+uuBvhE'
    'znUxIlfpfQ+Wu3ei39BRm8m1/uGkPLNPGcRaGVElRFZ+DJUXHsTyVutdB4/j6t+irnA2P1/Ziw6yWAJO'
    'hmQoqJTTviZAXDMey/5iNowoCdXiBH8n8NCl1WQWTqnCfk3eohWHD3iPJKK1WWZ8pSKguB+fDp45Tbo5'
    'Hoe1IjJdD1nYw5AwZ7MnMAxPPLujf/nrOe4aGRKjYoRaJBmW80vXl6phsH7c7yC5XI7OAHWOma2L4tdN'
    'p+10MWj0CE+2z0fw/RGp9/lXCc886CLRZAFyB2byTjZjBgzZq/iFIJKcl4jHRylhsbVHdvH4JEl63sXY'
    'BlOR9ayz3kPGRTZ7aTGgKXrYpbPkTP6xLdFg2hZ+4EZeJ/SJXNR/vBs6FbOmvUqL8Y3Wvzv002cvcVsz'
    'ctWGCKshocBRof19d+JhFwiJlfIn9mXlR63dViD6sSWYI5ukf2JsInee1TV5yaQQ8529vHBXM9KchlJO'
    'eyMpl/BUU4RydZrZvuKcnn/6r22rX3c+aE7LDFIkO1yfPcamlEvIsHvAFtZThv+DfD6nv/8H5hgk8VzS'
    'GRvNuo22zw+GIFAjnmz+ewo7LjbJ9uBmTfI7ECSrYJBHcHvit5teujPj7CArLwLVuCjFkCGiJJhTLGTE'
    '7roz+Xrt8SZtKNewsSJ8GArsGJdsDl06QX8wveIFu/REscZed2Upv4UIQUQx08PlDVIf6A+pVj3rfsSJ'
    '6Mbs3le8lOCWH54NhIrKOF1B465StvxujRMIh5wwi4oBMJvp+IzhewFlZzBZgASXdSLu9UHYznXgeckX'
    'b6FVy2CyWuZ2AMfS90yJMNm/LC6NlcKHzh3u0YiT5946+sRSfBWl5xfpOm4DRBiBqR5J3ado4brz09VO'
    'JTPJfRVX7Q6y0x4MTRCiqP2J1d8HPx7oFwGNcC1FlNcrhj+jxiwqmEuMWGMDibXiOIAiyfdmkOwhPehP'
    'XbH/Lsy+4nDHLIPewEhX8SCWCAQ7ClDPsupUX/sBTH2OzscIret1lTfHvL0+3Debx0yEkb0x412BQHVA'
    'rlB6AQDmDHySajmfdoi7XbiD89j6DJKhR0RJ4kBaj3kL4T7R2edgve6OWkaqI7829wg1saYFOT0RnZF7'
    'pDbVpNnjU92onIhWzosuShaPTfU='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
