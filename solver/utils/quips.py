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

A pool is deliberately deep — **32 subjects each, the same depth for every verb**, so that a
long run of regenerations does not read as the same commit repeated, and so no one verb's log
is wittier than another's. `commit_regenerated` picks uniformly at random with no memory of
the last pick, so depth is the only thing standing between the log and an obvious repeat.
Each subject is a lowercase sentence fragment, no trailing full stop: it is the tail of
`chore(update-docs): …`, not a sentence of its own.
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
        'the registry dictated; the guides took it down',
        'nobody typed this diff, and that is the point',
        'usage lines rebuilt from the signatures they describe',
        'the index and the code agree on what exists',
        'a catalogue is only as true as its last regeneration',
        'aliases, flags and arguments, as the decorator sees them',
        'what the shell will actually accept, written down',
        'the generated half; the written half was already fine',
        'docstrings escaped into the documentation',
        'the check that would have failed now passes',
        'no new prose, no lost prose, just current prose',
        'the manual stopped misdescribing the tool',
        'the command list, taken down from dictation',
        'between the markers, everything; outside them, nothing',
        'the commands changed shape and finally said so',
        'documentation is a snapshot; here is a fresher one',
        'help text, reunited with the help it describes',
        'the reference caught the rename it had missed',
        'a week of small renames, collected in one place',
        'the guides, re-derived rather than remembered',
        'every signature quoted back exactly as declared',
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
        'the price list expired; here is its successor',
        'tokens are cheaper somewhere and dearer elsewhere',
        'the enum learned this quarter\'s vocabulary',
        'a model retired; the pricing table noticed',
        'costs recomputed from a fresh JSON payload',
        'the API was asked what exists, and it answered',
        'input, output and cache, all three re-quoted',
        'sorted by price, because that is the useful order',
        'names change faster than the code that calls them',
        'a catalogue with a famously short shelf life',
        'the pricing page, transcribed without the adjectives',
        'newer, faster, cheaper — pick the two that are true',
        'members up, numbers down, block regenerated',
        'model IDs verbatim, so nothing is guessed at runtime',
        'the cost report now bills at current rates',
        'last month\'s frontier is this month\'s line item',
        'refreshed before anyone quoted the old price',
        'what we may ask for, and what asking costs',
        'a whole generation of models, filed',
        'the announcements landed; the enum caught up',
        'the tokens did not change; their price did',
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
        'the vocabulary and the corpus, in agreement',
        'no orphan tags, no unclaimed problems',
        'the ledger balanced from both directions',
        'counts recomputed, none invented',
        'facets swept, slugs sorted, refs rebuilt',
        'what the problems claim, the index now confirms',
        'the graph is a graph again',
        'every edge traversed from both of its ends',
        'the topics know which problems they cover',
        'reconciled: the tags say what the files say',
        'a tag with no problems was a tag with no purpose',
        'the vocabulary grew by exactly what was used',
        'proposals became tags; tags became links',
        'the index is the sum of its problems',
        'articles, tags and problems, mutually consistent',
        'bookkeeping, of the strictly double-entry kind',
        'the crosswalk rebuilt from the ground truth',
        'one pass, two legs, zero discrepancies',
        'the map of what connects to what, redrawn',
        'the graph audited itself and signed off',
        'every claim in the vocabulary now has a file behind it',
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
        'the central bank spoke; the constant listened',
        'a rate is true for a day, and this is that day',
        'the dollar drifted; the euro noticed',
        'foreign exchange, reduced to a single float',
        'costs restated in the currency that pays them',
        'Frankfurt\'s daily number, filed without comment',
        'the conversion factor stopped being stale',
        'yesterday\'s rate retired without ceremony',
        'the reference rate, as published at the usual hour',
        'dollars into euros, at this week\'s exchange',
        'the ledger, re-denominated',
        'exchange rates move; the setting should too',
        'the number that turns tokens into euros',
        'a fresh quote, before the stale one misled anyone',
        'the currency markets, summarised to four decimals',
        'the API spend, priced in the local money again',
        'the rate the central bank quotes, not the one a card would',
        'macro-economics, condensed to one line of Python',
        'the peg, re-pegged',
        'accurate this morning, approximate by lunch',
        'one line changed; every cost in the report moved',
    ),
}
