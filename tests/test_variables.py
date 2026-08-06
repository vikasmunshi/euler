#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Tests for the variable store, `@variable`, and the bridge to `Ask(choices=…)`.

The store had no tests of its own. What it guarantees is worth pinning: a user variable
can never clobber a special (that is the whole of the assign/set split), a registered
variable is *not* evaluated until referenced (the completer lists names beside a
`gh pr list` that must not run), and one declaration serves both a menu and a `loop`.

The last is the point of the bridge. A choice set used to be a callable that only the
dialogue could reach; naming a variable instead means `loop {open_prs}:` iterates the same
list the menu offers, and neither can drift from the other.
"""
from __future__ import annotations

import unittest
from typing import Any

from solver.shell.dialogue import Ask, Choice, as_choice
from solver.shell.variables import Variables, variable, variables


class _Pull(tuple[int, str]):
    """A stand-in for a domain object that knows how to offer itself in a menu."""

    def __choice__(self) -> Choice:
        return Choice(str(self[0]), f'#{self[0]}  {self[1]}', 'a branch')


class RegistrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = Variables()

    def test_a_registered_variable_is_reserved(self) -> None:
        self.store.define('widgets', lambda: [1, 2], 'some widgets', 'list[int]')
        self.assertIn('widgets', self.store['reserved'])
        with self.assertRaises(KeyError):
            self.store['widgets'] = 'mine'

    def test_a_seeded_special_cannot_be_registered_over(self) -> None:
        """Redefining `rcode` would rewrite what `&&` means, from an unrelated file."""
        for name in ('config', 'loop', 'problem', 'rcode', 'reserved'):
            with self.subTest(name=name), self.assertRaises(KeyError):
                self.store.define(name, lambda: None, 'no')

    def test_registration_records_what_the_docs_need(self) -> None:
        self.store.define('widgets', lambda: [1], 'some widgets', 'list[int]')
        info = self.store.info('widgets')
        assert info is not None
        self.assertEqual((info.kind, info.type_name, info.description),
                         ('computed', 'list[int]', 'some widgets'))

    def test_the_catalogue_covers_every_reserved_name(self) -> None:
        self.store.define('widgets', lambda: [1], 'some widgets')
        self.assertEqual({entry.name for entry in self.store.catalogue()},
                         set(self.store['reserved']))

    def test_a_user_variable_is_not_in_the_catalogue(self) -> None:
        self.store['mine'] = 1
        self.assertIsNone(self.store.info('mine'))


class DecoratorTests(unittest.TestCase):
    def test_the_function_is_returned_unchanged(self) -> None:
        """The same bargain `@register` keeps: still an ordinary callable."""
        @variable('a test value')
        def a_test_value() -> int:
            return 7

        self.addCleanup(_forget, 'a_test_value')
        self.assertEqual(a_test_value(), 7)
        self.assertEqual(variables['a_test_value'](), 7)

    def test_a_trailing_underscore_is_stripped(self) -> None:
        """`{next}` and `{problems}` are the names the language wants."""
        @variable('a value named for a builtin')
        def next_() -> int:
            return 1

        self.addCleanup(_forget, 'next')
        self.assertIn('next', variables['reserved'])

    def test_the_declared_return_type_is_recorded(self) -> None:
        @variable('a test value')
        def another_test_value() -> list[int]:
            return [1]

        self.addCleanup(_forget, 'another_test_value')
        info = variables.info('another_test_value')
        assert info is not None
        self.assertEqual(info.type_name, 'list[int]')


class LazinessTests(unittest.TestCase):
    """A registered variable is a callable in the store, invoked only when referenced."""

    def test_registering_does_not_evaluate(self) -> None:
        calls: list[int] = []

        @variable('counts its own reads')
        def counted() -> int:
            calls.append(1)
            return len(calls)

        self.addCleanup(_forget, 'counted')
        self.assertEqual(calls, [], 'registration must not read anything')
        self.assertTrue(callable(variables['counted']), 'the store holds the callable, not a value')
        variables['counted']()
        self.assertEqual(len(calls), 1)


class BuiltInVariableTests(unittest.TestCase):
    """The specials the store seeds, and the problem sets it registers."""

    def test_the_seeded_specials_are_all_reserved(self) -> None:
        for name in ('config', 'loop', 'problem', 'rcode', 'reserved'):
            with self.subTest(name=name), self.assertRaises(KeyError):
                variables[name] = 'mine'

    def test_the_problem_sets_are_registered_and_computed(self) -> None:
        for name in ('problems', 'solved', 'unsolved', 'last', 'next', 'random'):
            with self.subTest(name=name):
                info = variables.info(name)
                assert info is not None
                self.assertEqual(info.kind, 'computed')
                self.assertTrue(info.description, 'every variable says what it is')

    def test_every_catalogued_name_carries_a_description(self) -> None:
        for entry in variables.catalogue():
            with self.subTest(name=entry.name):
                self.assertTrue(entry.description)
                self.assertTrue(entry.type_name)


class AsChoiceTests(unittest.TestCase):
    def test_a_choice_passes_through(self) -> None:
        choice = Choice('v', 'label', 'description')
        self.assertIs(as_choice(choice), choice)

    def test_an_object_is_asked_how_to_show_itself(self) -> None:
        self.assertEqual(as_choice(_Pull((12, 'a title'))),
                         Choice('12', '#12  a title', 'a branch'))

    def test_anything_else_becomes_its_string_form(self) -> None:
        self.assertEqual(as_choice('u0a68e0'), Choice('u0a68e0'))
        self.assertEqual(as_choice(42), Choice('42'))


class NamedChoicesTests(unittest.TestCase):
    """`Ask(choices='name')` reads the variable, and renders whatever it holds."""

    def setUp(self) -> None:
        from solver.shell.register import _declared_choices
        self._resolve = _declared_choices

    def _choices(self, ask: Ask) -> list[Choice]:
        return self._resolve(ask, None, {})

    def test_a_named_variable_is_read_when_the_question_is_put(self) -> None:
        reads: list[int] = []

        @variable('the open widgets')
        def open_widgets() -> list[_Pull]:
            reads.append(1)
            return [_Pull((12, 'a title'))]

        self.addCleanup(_forget, 'open_widgets')
        ask = Ask('Which widget?', choices='open_widgets')
        self.assertEqual(reads, [], 'not read until asked')
        self.assertEqual(self._choices(ask), [Choice('12', '#12  a title', 'a branch')])
        self.assertEqual(len(reads), 1)

    def test_the_same_list_serves_a_loop_body(self) -> None:
        """The point of the bridge: the menu and `loop {…}` read one declaration."""
        @variable('the open widgets')
        def open_widgets() -> list[_Pull]:
            return [_Pull((12, 'a title'))]

        self.addCleanup(_forget, 'open_widgets')
        looped = variables['open_widgets']()
        self.assertEqual(looped[0][0], 12, 'the loop body sees the object, not a Choice')
        self.assertEqual(self._choices(Ask(choices='open_widgets'))[0].value, '12')

    def test_a_callable_still_works(self) -> None:
        ask = Ask(choices=lambda _ctx, _bound: [Choice('a')])
        self.assertEqual(self._choices(ask), [Choice('a')])

    def test_an_undefined_variable_is_named_in_the_error(self) -> None:
        with self.assertRaises(NameError) as caught:
            self._choices(Ask(choices='no_such_variable'))
        self.assertIn('no_such_variable', str(caught.exception))


def _forget(name: str) -> None:
    """Undo a registration made by a test, leaving the process-wide store as it was."""
    store: Any = variables
    store.__dict__.pop(name, None)
    store.__info__.pop(name, None)
    store.__reserved__.discard(name)
    store.__dict__['reserved'] = sorted(store.__reserved__)


if __name__ == '__main__':
    unittest.main()
