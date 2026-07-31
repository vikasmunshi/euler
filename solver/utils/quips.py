#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The `update-*` verbs' commit subjects — one pool per verb, in one place.

Every regenerating verb lands its own output through
:func:`~solver.core.git.commit_regenerated`, which writes `chore(<verb>): <quip>` over a body
naming what actually moved. The wit is the caller's, so each verb needs a pool of subjects to
pick from — and four modules each grew their own private `_QUIPS` tuple, which put the same
kind of thing in four places and let the pools drift apart in size and voice.

They live here instead, keyed by the same verb name `commit_regenerated` is called with (and
that :data:`~solver.core.git.GENERATED_PATHS` keys its staging scope by). The `Quips`
TypedDict is what keeps the two in step: a key that is not a verb, or a verb that has no pool,
is a type error rather than a `KeyError` on the day someone regenerates something.

A pool is deliberately deep — ten-plus subjects each, so a run of regenerations does not read
as the same commit repeated. Each is a lowercase sentence fragment, no trailing full stop:
it is the tail of `chore(update-docs): …`, not a sentence of its own.
"""
from __future__ import annotations

__all__ = ['Quips', 'quips']

from typing import TypedDict

#: The commit-subject pools, one per regenerating verb. Keys are the verb names
#: `commit_regenerated` takes — the same keys as `solver.core.git.GENERATED_PATHS`.
Quips = TypedDict('Quips', {
    'update-docs': tuple[str, ...],
    'update-models': tuple[str, ...],
    'update-tags': tuple[str, ...],
    'update-usd-rate': tuple[str, ...],
})

quips: Quips = {
    'update-docs': (
        'the map, redrawn to match the territory',
        'the docs now describe the software that exists',
        'the catalogue remembers what the registry knows',
        'prose left alone; the generated blocks tidied themselves',
        'documentation caught up with the code it documents',
        'every command, described as it is currently registered',
        'the guides re-read the registry and changed their minds',
        'markers refilled; the words between them untouched',
        'the reference stopped describing last week',
        'the table of contents of a moving target',
        'generated blocks, regenerated; nothing else moved',
    ),
    'update-models': (
        'the frontier moved again; the enum followed',
        'new models, new prices, same generated block',
        're-priced: what a million tokens costs this week',
        'the catalogue, as the API currently tells it',
        'models come, models go, the markers stay put',
        'the enum, refreshed from whoever is shipping today',
        'per-token arithmetic, straight from the pricing page',
        'the model list stopped being a historical document',
        'comments kept, members rewritten, order by price',
        'what the Models API says exists, said in Python',
        'this is the catalogue; it will not be for long',
    ),
    'update-tags': (
        'both legs of the double entry agree again',
        'the tag graph balances',
        'vocabulary and problems, reconciled',
        'every tag knows its problems; every problem knows its tags',
        'the index caught up with the articles',
        'proposals promoted; refs rebuilt from the files',
        'the graph closed its books',
        'one pass over the vocabulary, and nothing dangles',
        'articles listed, counted, and stamped',
        'the double entry, entered twice as intended',
        'slugs filed under the facets they actually belong to',
    ),
    'update-usd-rate': (
        'the euro moved, so the ledger moved',
        're-pegged to Frankfurt\'s opinion of the dollar',
        'one float, imported fresh from the ECB',
        'money is a moving target; this is where it moved to',
        'today\'s exchange rate, before it stops being today\'s',
        'the reference rate, referenced again',
        'one number, and the cost report believes it',
        'the dollar, priced in euros, as of this morning',
        'currency drift, formally acknowledged',
        'a fourth decimal place changed hands',
        'the ECB published; the setting followed',
    ),
}
