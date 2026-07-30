#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Tests for solver.utils.doclint — the command-docstring standard (developer-guide §3.8).

Each test builds a throwaway function with a crafted docstring and signature, wraps it in a
`Command`, and asserts which rules `check` reports. The registry is never touched, so the
rules are tested independently of what happens to be registered for the running subject.
"""
from __future__ import annotations

import unittest

from solver.core.problems import Problem
from solver.shell.command import Command, Context
from solver.shell.builtins import _prose
from solver.shell.docstring import (GLYPH_PROBLEM, GLYPH_REQUIRES, GLYPH_SILENT, HelpModel,
                                    NOTE_PROBLEM, NOTE_SILENT, SILENT_HELP, entries,
                                    help_model, requires_note, sections)
from solver.utils.doclint import MAX_WIDTH, check


def _rules(func: object, name: str = 'demo') -> list[str]:
    """The rule names `check` reports for a function's docstring, in reading order."""
    return [f.rule for f in check(Command(name=name, func=func))]  # type: ignore[arg-type]


class ConformingTests(unittest.TestCase):
    def test_a_conforming_docstring_reports_nothing(self) -> None:
        def cmd(ctx: Context, problem: Problem, runs: int = 1, *categories: str) -> int:
            """Evaluate the solutions of a problem.

            Prose explaining what it does and when to reach for it.

            Args:
                ctx: [injected] The live shell context; the decorator supplies it.
                problem: [problem] The problem to evaluate. A bare number, or omitted to
                    use the current problem.
                runs: How many times to run each solution. Defaults to 1.
                *categories: Test-case categories to include. Defaults to 'dev'.

            Notes:
                A free section is allowed and is not read as arguments.
            """
            return 0

        self.assertEqual([], _rules(cmd))

    def test_a_command_without_parameters_needs_no_args_section(self) -> None:
        def cmd() -> int:
            """Report the running build's version."""
            return 0

        self.assertEqual([], _rules(cmd))

    def test_throwaway_parameters_are_exempt(self) -> None:
        def cmd(*_: str) -> int:
            """Clear the screen."""
            return 0

        self.assertEqual([], _rules(cmd))


class SummaryTests(unittest.TestCase):
    def test_missing_docstring(self) -> None:
        def cmd() -> int:
            return 0

        self.assertEqual(['missing-docstring'], _rules(cmd))

    def test_summary_must_end_with_a_period(self) -> None:
        def cmd() -> int:
            """Report the version"""
            return 0

        self.assertEqual(['summary'], _rules(cmd))

    def test_summary_must_be_one_line(self) -> None:
        def cmd() -> int:
            """Report the version of the running build, which spills onto
            a second line with no blank line between.
            """
            return 0

        self.assertIn('summary', _rules(cmd))

    def test_the_summary_fits_a_catalogue_cell(self) -> None:
        def cmd() -> int:
            """Report the version."""
            return 0

        # Between the two budgets: too wide for a catalogue cell, still inside the panel.
        cmd.__doc__ = 'Report the version of the running build, at length but not too much.'.ljust(90, '.')
        self.assertEqual(['summary-length'], _rules(cmd))

    def test_inline_code_uses_single_backticks(self) -> None:
        def cmd() -> int:
            """Report the version.

            Reads ``version.py``, the source of truth.
            """
            return 0

        self.assertEqual(['rst-literal'], _rules(cmd))

    def test_rendered_lines_stay_under_the_panel_width(self) -> None:
        def cmd() -> int:
            """Report the version."""
            return 0

        cmd.__doc__ = f'Report the version.\n\n{"x" * (MAX_WIDTH + 1)}\n'
        self.assertEqual(['line-length'], _rules(cmd))


class SectionTests(unittest.TestCase):
    def test_returns_and_raises_are_boilerplate(self) -> None:
        def cmd() -> int:
            """Report the version.

            Returns:
                The exit code.

            Raises:
                OSError: never, in practice.
            """
            return 0

        self.assertEqual(['banned-section', 'banned-section'], _rules(cmd))

    def test_the_parameter_section_is_spelled_args(self) -> None:
        def cmd(target: str) -> int:
            """Set up a target.

            Parameters:
                target: What to set up.
            """
            return 0

        self.assertEqual(['banned-section', 'args-section'], _rules(cmd))

    def test_args_section_required_when_the_command_takes_parameters(self) -> None:
        def cmd(details: bool = False) -> int:
            """List the tags."""
            return 0

        self.assertEqual(['args-section'], _rules(cmd))

    def test_args_section_refused_when_the_command_takes_none(self) -> None:
        def cmd() -> int:
            """Report the version.

            Args:
                nothing: There is no such parameter.
            """
            return 0

        self.assertIn('args-section', _rules(cmd))


class ArgumentTests(unittest.TestCase):
    def test_every_parameter_must_be_described(self) -> None:
        def cmd(first: str, second: str = '') -> int:
            """Do a thing.

            Args:
                first: The first thing.
            """
            return 0

        self.assertEqual(['undocumented'], _rules(cmd))

    def test_a_described_non_parameter_is_reported(self) -> None:
        def cmd(first: str) -> int:
            """Do a thing.

            Args:
                first: The first thing.
                Note: this stray line parses as an argument.
            """
            return 0

        self.assertEqual(['unknown-arg'], _rules(cmd))

    def test_arguments_follow_the_signature_order(self) -> None:
        def cmd(first: str, second: str = '') -> int:
            """Do a thing.

            Args:
                second: The second thing.
                first: The first thing.
            """
            return 0

        self.assertEqual(['arg-order'], _rules(cmd))

    def test_an_entry_without_prose_counts_as_undocumented(self) -> None:
        def cmd(first: str) -> int:
            """Do a thing.

            Args:
                first:
            """
            return 0

        self.assertEqual(['empty-description'], _rules(cmd))

    def test_variadics_keep_their_stars(self) -> None:
        def cmd(*categories: str) -> int:
            """Do a thing.

            Args:
                categories: The categories.
            """
            return 0

        self.assertEqual(['arg-name'], _rules(cmd))


class IndentTests(unittest.TestCase):
    def test_descriptions_are_not_aligned_into_a_column(self) -> None:
        def cmd(first: str, second: str = '') -> int:
            """Do a thing.

            Args:
                first:      The first thing, aligned into a column and wrapped
                            under that column rather than four past the name.
                second:     The second thing.
            """
            return 0

        self.assertEqual(['indent'], _rules(cmd))

    def test_a_wrapped_description_indents_four_past_its_entry(self) -> None:
        def cmd(first: str) -> int:
            """Do a thing.

            Args:
                first: The first thing, wrapped
                    four columns past the name.
            """
            return 0

        self.assertEqual([], _rules(cmd))


class MarkerTests(unittest.TestCase):
    def test_the_injected_context_must_be_marked(self) -> None:
        def cmd(ctx: Context) -> int:
            """Do a thing.

            Args:
                ctx: The command context.
            """
            return 0

        self.assertEqual(['marker'], _rules(cmd))

    def test_the_problem_special_must_be_marked(self) -> None:
        def cmd(problem: Problem) -> int:
            """Do a thing.

            Args:
                problem: The problem to act on.
            """
            return 0

        self.assertEqual(['marker'], _rules(cmd))

    def test_an_optional_problem_is_still_the_problem_special(self) -> None:
        def cmd(problem: Problem | None = None) -> int:
            """Do a thing.

            Args:
                problem: [problem] The problem to act on, or the current one.
            """
            return 0

        self.assertEqual([], _rules(cmd))

    def test_an_ordinary_argument_takes_no_marker(self) -> None:
        def cmd(runs: int = 1) -> int:
            """Do a thing.

            Args:
                runs: [injected] How many times. Defaults to 1.
            """
            return 0

        self.assertEqual(['marker'], _rules(cmd))


class HelpModelTests(unittest.TestCase):
    """The model `?` renders and `update-docs` publishes (solver/shell/docstring)."""

    def _model(self, *, quietable: bool = False, uses_problem: bool = False) -> HelpModel:
        def cmd(ctx: Context, problem: Problem, runs: int = 1) -> int:
            """Do a thing.

            Prose about the thing.

            Args:
                ctx: [injected] The live shell context; the decorator supplies it.
                problem: [problem] The problem to act on.
                runs: How many times. Defaults to 1.

            Notes:
                A free section.
            """
            return 0

        command = Command(name='demo', func=cmd, help='Do a thing.', usage='\tdemo',
                          requires='contributor', quietable=quietable, uses_problem=uses_problem)
        return help_model(command)

    def test_the_floor_is_stated_as_a_fact(self) -> None:
        self.assertIn((GLYPH_REQUIRES, 'needs contributor or above.'), self._model().notes)

    def test_the_top_rung_has_nothing_above_it(self) -> None:
        self.assertEqual('needs admin.', requires_note('admin'))

    def test_the_injected_context_is_not_an_argument(self) -> None:
        self.assertEqual(['problem', 'runs'], [name for name, _ in self._model().arguments])

    def test_a_quietable_command_gains_the_silent_row(self) -> None:
        model = self._model(quietable=True)
        self.assertEqual(('silent', SILENT_HELP), model.arguments[-1])
        self.assertIn((GLYPH_SILENT, NOTE_SILENT), model.notes)

    def test_the_problem_special_is_noted(self) -> None:
        self.assertIn((GLYPH_PROBLEM, NOTE_PROBLEM), self._model(uses_problem=True).notes)

    def test_markers_are_stripped_from_the_descriptions(self) -> None:
        arguments = dict(self._model().arguments)
        self.assertEqual('The problem to act on.', arguments['problem'])

    def test_prose_excludes_the_summary_and_the_sections(self) -> None:
        model = self._model()
        self.assertEqual('Prose about the thing.', model.prose)
        self.assertEqual([('notes', 'A free section.')], model.sections)


class ParsingTests(unittest.TestCase):
    def test_sections_split_lead_from_titled_bodies(self) -> None:
        lead, found = sections('Summary.\n\nProse.\n\nArgs:\n    a: one\n\nNotes:\n    free\n')
        self.assertEqual(['Summary.', '', 'Prose.', ''], lead)
        self.assertEqual(['args', 'notes'], list(found))

    def test_continuation_lines_join_the_entry_above(self) -> None:
        parsed = entries(['    first: one line', '        wrapped on: a colon', '    second: two'])
        self.assertEqual([('first', 'one line wrapped on: a colon'), ('second', 'two')], parsed)


class RenderTests(unittest.TestCase):
    """The `?` renderer's docstring handling (solver/shell/builtins)."""

    def test_inline_code_survives_both_spellings(self) -> None:
        rendered = _prose('markdown `one` and rst ``two`` and **three**').plain
        self.assertEqual('markdown one and rst two and three', rendered)

    def test_bracketed_text_is_never_read_as_markup(self) -> None:
        self.assertEqual('[injected] stays', _prose('[injected] stays').plain)

    def test_prose_is_rewrapped_but_literal_blocks_are_not(self) -> None:
        rendered = _prose('one line\nwrapped for the source\n\n    a = literal\n    b = block').plain
        self.assertEqual('one line wrapped for the source\n\n    a = literal\n    b = block', rendered)

    def test_a_bullet_list_keeps_its_line_breaks(self) -> None:
        self.assertEqual('- first\n- second', _prose('- first\n- second').plain)


if __name__ == '__main__':
    unittest.main()
