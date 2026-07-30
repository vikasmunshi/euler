#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Tests for the shared interaction model: solver/shell/dialogue.py and the `Ask` binding.

Two seams stand in for a terminal: `dialogue.interactive`, the one guard every prompt goes
through, and the shared console's `input`. Scripting both lets a dialogue be driven exactly as
a user would drive it — which is also how the commands under `tests/test_git_commands.py` and
`tests/test_tags.py` test their walks.

The non-interactive half matters as much: before this module, a prompt with a pipe on stdin
dumped an `EOFError` traceback, and every `confirm()` site (including `key-rekey`) could hit it.
"""
from __future__ import annotations

import unittest
from typing import Annotated, Any, Literal
from unittest.mock import patch

from solver.config import ExitCodes
from solver.shell import dialogue
from solver.shell.command import Context, registry
from solver.shell.dialogue import SKIP, Abort, Action, Ask, Choice
from solver.shell.register import register
from solver.shell.tty import console

_OPTIONS = [Choice('list', 'list', 'your threads'),
            Choice('read', 'read', 'open one thread'),
            Choice('send', 'send', 'ask staff')]


class _DialogueCase(unittest.TestCase):
    """Drives the dialogues through the two seams, with output swallowed."""

    def script(self, *answers: str) -> None:
        """Answer the next prompts with *answers*, as a user typing them would."""
        queue = list(answers)
        patcher = patch.object(dialogue, 'interactive', lambda: True)
        patcher.start()
        self.addCleanup(patcher.stop)

        def read(*_: object, **__: object) -> str:
            # An exhausted script behaves like a real terminal at EOF — raising, not returning
            # '' for ever, which would spin any prompt that re-asks on an empty answer.
            if not queue:
                raise EOFError('the script ran out of answers')
            return queue.pop(0)

        reader = patch.object(console, 'input', read)
        reader.start()
        self.addCleanup(reader.stop)
        quiet = patch.object(console, 'quiet', True)     # swallow the rendering, keep the reads
        quiet.start()
        self.addCleanup(quiet.stop)

    def non_interactive(self) -> None:
        """No tty, no terminal — a piped block or `< /dev/null`."""
        patcher = patch.object(dialogue, 'interactive', lambda: False)
        patcher.start()
        self.addCleanup(patcher.stop)


class ConfirmTests(_DialogueCase):
    def test_enter_takes_the_default(self) -> None:
        self.script('', '')
        self.assertTrue(dialogue.confirm('go?', default=True))
        self.assertFalse(dialogue.confirm('go?', default=False))

    def test_only_y_agrees(self) -> None:
        self.script('y', 'yes', 'n', 'nope')
        self.assertTrue(dialogue.confirm('go?'))
        self.assertTrue(dialogue.confirm('go?'))
        self.assertFalse(dialogue.confirm('go?'))
        self.assertFalse(dialogue.confirm('go?'))

    def test_non_interactive_aborts_as_a_usage_error(self) -> None:
        """The crash class: this used to be an `EOFError` traceback."""
        self.non_interactive()
        with self.assertRaises(Abort) as caught:
            dialogue.confirm('go?')
        self.assertEqual(ExitCodes.EXIT_USAGE, caught.exception.rc)

    def test_a_caller_may_declare_what_to_assume(self) -> None:
        self.non_interactive()
        self.assertFalse(dialogue.confirm('go?', assume=False))


class SureTests(_DialogueCase):
    def test_the_phrase_must_be_typed(self) -> None:
        self.script('rekey')
        self.assertTrue(dialogue.sure('rotate?', phrase='rekey'))

    def test_anything_else_declines(self) -> None:
        self.script('yes', '', 'y')
        for _ in range(3):
            self.assertFalse(dialogue.sure('rotate?', phrase='rekey'))

    def test_case_does_not_matter(self) -> None:
        self.script('ReKey')
        self.assertTrue(dialogue.sure('rotate?', phrase='rekey'))

    def test_it_cannot_be_answered_non_interactively(self) -> None:
        """No `assume` escape: a destructive act is never agreed to by default."""
        self.non_interactive()
        with self.assertRaises(Abort):
            dialogue.sure('rotate?', phrase='rekey')


class PauseTests(_DialogueCase):
    def test_a_pause_with_nobody_waiting_is_a_no_op(self) -> None:
        self.non_interactive()
        self.assertIsNone(dialogue.pause())


class ChooseTests(_DialogueCase):
    def test_a_number_picks_the_option(self) -> None:
        self.script('2')
        self.assertEqual('read', dialogue.choose('what?', _OPTIONS))

    def test_the_value_may_be_typed_out(self) -> None:
        self.script('send')
        self.assertEqual('send', dialogue.choose('what?', _OPTIONS))

    def test_enter_takes_the_default(self) -> None:
        self.script('')
        self.assertEqual('list', dialogue.choose('what?', _OPTIONS, default='list'))

    def test_quitting_aborts(self) -> None:
        self.script('q')
        with self.assertRaises(Abort) as caught:
            dialogue.choose('what?', _OPTIONS)
        self.assertEqual(ExitCodes.EXIT_ABORT, caught.exception.rc)

    def test_a_bad_answer_is_re_asked(self) -> None:
        self.script('9', 'nonsense', '1')
        self.assertEqual('list', dialogue.choose('what?', _OPTIONS))

    def test_an_empty_option_set_says_so(self) -> None:
        """The emptiness is the answer — what a prefix-filtering completer cannot tell you."""
        self.script()
        with self.assertRaises(Abort) as caught:
            dialogue.choose('which message?', [], empty='no messages')
        self.assertEqual('no messages', caught.exception.message)
        self.assertEqual(ExitCodes.EXIT_ERROR, caught.exception.rc)

    def test_a_long_list_becomes_a_search(self) -> None:
        many = [Choice(f'p{n:04d}', f'p{n:04d}', f'problem {n}') for n in range(1, 40)]
        self.script('0037', '1')
        self.assertEqual('p0037', dialogue.choose('which problem?', many))

    def test_a_lax_choice_accepts_what_was_typed(self) -> None:
        self.script('something-else')
        self.assertEqual('something-else', dialogue.choose('what?', _OPTIONS, strict=False))


class SelectTests(_DialogueCase):
    def test_search_toggle_done(self) -> None:
        self.script('open', '1', 'done')            # matches read's description alone
        self.assertEqual(['read'], dialogue.select('which?', _OPTIONS))

    def test_a_second_toggle_removes(self) -> None:
        self.script('open', '1', '1', 'staff', '1', 'done')
        self.assertEqual(['send'], dialogue.select('which?', _OPTIONS))

    def test_done_with_nothing_selected_keeps_asking(self) -> None:
        self.script('done', 'staff', '1', 'done')
        self.assertEqual(['send'], dialogue.select('which?', _OPTIONS))

    def test_quitting_aborts(self) -> None:
        self.script('q')
        with self.assertRaises(Abort):
            dialogue.select('which?', _OPTIONS)


class WalkTests(_DialogueCase):
    def setUp(self) -> None:
        self.done: list[str] = []
        self.actions = {'m': Action('merge', lambda item: self.done.append(str(item))),
                        's': Action('skip', SKIP)}

    def test_every_item_is_offered_in_order(self) -> None:
        self.script('m', 's', 'm')
        result = dialogue.walk(['a', 'b', 'c'], self.actions, render=str)
        self.assertEqual(['a', 'c'], self.done)
        self.assertEqual({'merge': 2, 'skip': 1}, result.counts)
        self.assertEqual(ExitCodes.EXIT_OK, result.rc)

    def test_quitting_stops_the_walk_and_is_an_abort(self) -> None:
        self.script('m', 'q')
        result = dialogue.walk(['a', 'b', 'c'], self.actions, render=str)
        self.assertEqual(['a'], self.done)
        self.assertTrue(result.quit)
        self.assertEqual(ExitCodes.EXIT_ABORT, result.rc)

    def test_an_unknown_key_leaves_the_item_alone(self) -> None:
        self.script('x', 'm')
        result = dialogue.walk(['a', 'b'], self.actions, render=str)
        self.assertEqual(['b'], self.done)
        self.assertEqual(1, result.counts['untouched'])

    def test_an_empty_queue_is_a_clean_no_op(self) -> None:
        self.non_interactive()
        result = dialogue.walk([], self.actions, render=str)
        self.assertEqual(ExitCodes.EXIT_OK, result.rc)

    def test_a_walk_needs_somebody_to_ask(self) -> None:
        self.non_interactive()
        with self.assertRaises(Abort) as caught:
            dialogue.walk(['a'], self.actions, render=str)
        self.assertEqual(ExitCodes.EXIT_USAGE, caught.exception.rc)

    def test_q_cannot_be_taken_as_an_action_key(self) -> None:
        with self.assertRaises(ValueError):
            dialogue.walk(['a'], {'q': Action('quit', SKIP)}, render=str)


class TextTests(_DialogueCase):
    def test_an_empty_answer_is_re_asked(self) -> None:
        self.script('', 'something')
        self.assertEqual('something', dialogue.text('subject'))

    def test_a_default_is_taken_by_enter(self) -> None:
        self.script('')
        self.assertEqual('fallback', dialogue.text('subject', default='fallback'))

    def test_validation_re_asks_with_the_reason(self) -> None:
        def digits(answer: str) -> str | None:
            return None if answer.isdigit() else 'digits only'

        self.script('abc', '42')
        self.assertEqual('42', dialogue.text('how many', validate=digits))

    def test_multiline_reads_until_a_blank_line(self) -> None:
        self.script('first', 'second', '')
        self.assertEqual('first\nsecond', dialogue.text('body', multiline=True))


class InteractiveGuardTests(unittest.TestCase):
    """The guard itself: three conditions, all necessary."""

    def test_silent_makes_a_shell_non_interactive(self) -> None:
        """A quietable command in a pipeline must never block on a question nobody can see."""
        with (patch('sys.stdin.isatty', lambda: True),
              patch.object(console, 'is_interactive', True),
              patch.object(console, 'quiet', True)):
            self.assertFalse(dialogue.interactive())
        with (patch('sys.stdin.isatty', lambda: True),
              patch.object(console, 'is_interactive', True),
              patch.object(console, 'quiet', False)):
            self.assertTrue(dialogue.interactive())

    def test_a_pipe_on_stdin_is_not_interactive(self) -> None:
        with patch('sys.stdin.isatty', lambda: False):
            self.assertFalse(dialogue.interactive())


# ── model 1: the adapter asking for what was left out ───────────────────────────────────

def _colours(_: Context, bound: dict[str, Any]) -> list[Choice]:
    """A live choice set that narrows by an earlier answer, as `msg`'s threads do."""
    if bound.get('mode') == 'warm':
        return [Choice('red'), Choice('orange')]
    return [Choice('red'), Choice('orange'), Choice('blue')]


class AskTests(_DialogueCase):
    """`Annotated[T, Ask(...)]` — declared on the parameter, served by the adapter."""

    @classmethod
    def setUpClass(cls) -> None:
        @register(requires='reader')
        def ask_demo(mode: Annotated[Literal['warm', 'cool'], Ask('Which mode?')] = 'cool',
                     colour: Annotated[str, Ask('Which colour?', choices=_colours)] = '',
                     note: Annotated[str, Ask('A note?',
                                              when=lambda bound: bound['mode'] == 'warm')] = '',
                     count: int = 1) -> int:
            """Demo command for the Ask binding.

            Args:
                mode: [asked] Which mode.
                colour: [asked] Which colour.
                note: [asked] A note.
                count: How many. Defaults to 1.
            """
            cls.calls.append({'mode': mode, 'colour': colour, 'note': note, 'count': count})
            return ExitCodes.EXIT_OK

        cls.command = registry.resolve('ask-demo')
        cls.calls: list[dict[str, Any]] = []

    @classmethod
    def tearDownClass(cls) -> None:
        registry.unregister('ask-demo')

    def _invoke(self, *argv: str) -> int:
        self.calls.clear()
        assert self.command is not None
        return self.command.invoke(Context(argv=list(argv)))

    def test_what_the_user_typed_is_never_asked_for(self) -> None:
        self.script('2')                                     # would answer 'Which colour?'
        self.assertEqual(ExitCodes.EXIT_OK, self._invoke('cool', 'colour=blue'))
        self.assertEqual([{'mode': 'cool', 'colour': 'blue', 'note': '', 'count': 1}], self.calls)

    def test_a_literal_becomes_a_menu_with_no_callable(self) -> None:
        self.script('1', '1', 'a note')                      # mode → warm, colour → red, note
        self._invoke()
        self.assertEqual('warm', self.calls[0]['mode'])
        self.assertEqual('red', self.calls[0]['colour'])

    def test_choices_see_the_earlier_answers(self) -> None:
        """'blue' is not offered in warm mode — so index 3 is out of range and re-asked."""
        self.script('1', '3', '2', 'a note')
        self._invoke()
        self.assertEqual('orange', self.calls[0]['colour'])

    def test_when_decides_whether_to_ask_at_all(self) -> None:
        self.script('2', '1')                                # cool → note is not asked
        self._invoke()
        self.assertEqual('', self.calls[0]['note'])

    def test_nothing_is_asked_non_interactively(self) -> None:
        """A scripted block behaves exactly as it did before the command declared any Ask."""
        self.non_interactive()
        self.assertEqual(ExitCodes.EXIT_OK, self._invoke())
        self.assertEqual([{'mode': 'cool', 'colour': '', 'note': '', 'count': 1}], self.calls)

    def test_quitting_a_question_aborts_the_command(self) -> None:
        self.script('q')
        self.assertEqual(ExitCodes.EXIT_ABORT, self._invoke())
        self.assertEqual([], self.calls)

    def test_the_usage_line_marks_an_asked_argument(self) -> None:
        assert self.command is not None
        self.assertIn('[colour=<str>] (asked)', self.command.usage)
        self.assertIn('[count=<int>] (default 1)', self.command.usage)

    def test_the_command_records_that_it_asks(self) -> None:
        assert self.command is not None
        self.assertTrue(self.command.asks)

    def test_choices_also_drive_completion(self) -> None:
        """One declaration, both surfaces — the menu and the tab-completion."""
        assert self.command is not None and self.command.completer is not None
        offered = self.command.completer(Context(argv=['colour=b']), 'colour=b')
        self.assertEqual(['colour=blue'], [str(c.text) for c in offered])  # type: ignore[union-attr]


class MsgNoDeadEndTests(_DialogueCase):
    """No verb may ask for some answers and then refuse for one it never asked about.

    The defect this pins: `msg notice` walked the user through subject and message, then failed
    with `needs to=… or --all` — an argument no question had offered, naming a flag that did not
    exist. A verb that asks must ask for everything the path it took needs.
    """

    def setUp(self) -> None:
        from solver.web.auth import commands as auth_commands
        from solver.web.msg import commands as msg_commands
        self.commands = msg_commands
        self.calls: list[tuple[str, Any]] = []
        # The spool is not reachable under test: every verb's own call is stubbed to succeed,
        # so what remains is the argument-gathering this test is about.
        thread = {'id': 'abc123', 'subject': 'a thread', 'author_name': 'staff',
                  'updated': '2026-07-30T09:00', 'unread': True}
        self.enterContext(patch.object(
            msg_commands, '_call',
            lambda verb, **kw: (self.calls.append((verb, kw)),
                                (200, {'threads': [thread], 'queue': [thread]}))[1]))
        self.enterContext(patch.object(msg_commands, '_is_staff', lambda: True))
        # `Ask(choices=fn)` captures the function *by value* at decoration time, so patching
        # `_threads` / `_recipients` by name would not be seen. Stub what they read instead.
        self.enterContext(patch.object(auth_commands, 'account_identities', lambda: ['a@x.com']))

    def _verb(self, verb: str, *answers: str) -> int:
        """Run one verb through the adapter, answering as a user would.

        Through the registry, not by calling `msg()` directly: the `Ask` binding lives in the
        adapter, and a command function stays a plain callable that asks nothing.
        """
        self.script(*answers)
        command = registry.resolve('msg')
        assert command is not None
        return command.invoke(Context(argv=[verb]))

    def test_notice_asks_for_its_recipients(self) -> None:
        rc = self._verb('notice', 'a subject', 'the body', '', '1')
        self.assertNotEqual(ExitCodes.EXIT_USAGE, rc, 'a notice must never ask then refuse')
        self.assertIn('notice', [verb for verb, _ in self.calls])

    def test_the_recipient_question_is_what_prevents_the_dead_end(self) -> None:
        """Take the question away and the defect returns — which is what this class pins.

        The adapter closes over the command's `_CommandSpec`, so dropping `to` from its `asks`
        reproduces exactly what shipped: subject and message asked for, then a usage error
        about an argument no question offered.
        """
        command = registry.resolve('msg')
        assert command is not None
        spec = next(cell.cell_contents for cell in (command.func.__closure__ or ())
                    if type(cell.cell_contents).__name__ == '_CommandSpec')
        without_to = {name: ask for name, ask in spec.asks.items() if name != 'to'}
        with patch.object(spec, 'asks', without_to):
            self.script('a subject', 'the body', '')          # '' ends the multiline message
            self.assertEqual(ExitCodes.EXIT_USAGE, command.invoke(Context(argv=['notice'])))

    def test_send_asks_for_subject_and_body(self) -> None:
        rc = self._verb('send', 'a subject', 'the body', '')
        self.assertNotEqual(ExitCodes.EXIT_USAGE, rc)
        self.assertIn('send', [verb for verb, _ in self.calls])

    def test_the_thread_verbs_ask_for_a_thread(self) -> None:
        for verb in ('read', 'save', 'dismiss'):
            with self.subTest(verb=verb):
                try:
                    rc = self._verb(verb, '1')
                except Abort as abort:                       # a refusal is fine; a *usage* one is not
                    rc = abort.rc
                self.assertNotEqual(ExitCodes.EXIT_USAGE, rc, f'{verb} must not ask then refuse')


if __name__ == '__main__':
    unittest.main()
