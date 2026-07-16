#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The one-time shell ticket — the masquerade guard for the web shell.

Every web shell runs as the shared ``euler-ws-<profile>`` uid and
``/proc/<pid>/environ`` is same-uid-readable, so nothing carried in the
environment can be a reusable credential. Identity therefore transfers by a
**consumable** ticket: minted against a live session, redeemed once at fork.
This pins the properties the masquerade story rests on — single-use (a replay
from a sibling shell's environ is dead on arrival), time-boxed, and bound to
the exact identity it was minted for. The kernel-side guards (a service uid with
no ticket aborts; a ticket whose profile ≠ the instance pin aborts) live in
``test_auth_kernel``; the app-side refusals in ``test_ws``."""
from __future__ import annotations

import unittest

from solver.web.auth.tickets import TicketStore


class TicketStoreTests(unittest.TestCase):

    def test_redeem_returns_the_bound_identity(self) -> None:
        store = TicketStore()
        ticket = store.mint('User@Example.com', 'contributor')
        self.assertEqual(store.redeem(ticket), ('user@example.com', 'contributor'))

    def test_ticket_is_single_use(self) -> None:
        """The replay guard: a second redeem of the same ticket fails — so a sibling
        shell replaying it from /proc/<pid>/environ gets nothing."""
        store = TicketStore()
        ticket = store.mint('u@example.com', 'reader')
        self.assertIsNotNone(store.redeem(ticket))       # the victim's own startup
        self.assertIsNone(store.redeem(ticket))          # the replay — dead on arrival

    def test_unknown_ticket_is_rejected(self) -> None:
        store = TicketStore()
        self.assertIsNone(store.redeem('never-minted'))

    def test_ticket_expires(self) -> None:
        """A ticket past its TTL is not redeemable (minting and forking are
        back-to-back; a stale one cannot be used)."""
        store = TicketStore(ttl_seconds=0)               # already expired on mint
        ticket = store.mint('u@example.com', 'maintainer')
        self.assertIsNone(store.redeem(ticket))

    def test_tickets_are_distinct_and_independently_consumed(self) -> None:
        store = TicketStore()
        first = store.mint('a@example.com', 'reader')
        second = store.mint('b@example.com', 'maintainer')
        self.assertNotEqual(first, second)
        self.assertEqual(store.redeem(second), ('b@example.com', 'maintainer'))
        self.assertEqual(store.redeem(first), ('a@example.com', 'reader'))   # unaffected

    def test_ticket_is_stored_hashed_not_in_the_clear(self) -> None:
        """The raw token is the credential; the store keeps only its hash, so a read
        of the store's memory does not yield a redeemable ticket."""
        store = TicketStore()
        ticket = store.mint('u@example.com', 'reader')
        self.assertNotIn(ticket, store._tickets)         # noqa: SLF001 — the raw token is not a key
        self.assertTrue(store._tickets)                  # …but something is stored (the hash)


if __name__ == '__main__':
    unittest.main()
