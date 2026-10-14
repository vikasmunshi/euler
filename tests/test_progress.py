#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Tests for the progress page parser: one tooltip cell → one `problems.json` record."""
from __future__ import annotations

import unittest

from datetime import UTC, datetime

from solver.core.progress import format_solved_date, parse_progress, parse_solved_date

_SOLVED = ('<td class="tooltip problem_solved t_0"><a href="problem=1">&nbsp;1&nbsp;'
           '<span class="tooltiptext_narrow"><div class="strong larger">Problem 1</div>'
           '<div>Solved by 864300</div><div class="smaller">Difficulty: Level 0 [1%]</div>'
           '<div class="smaller">Completed on Thu, 2 Jul 2015, 17:16</div>'
           '<div>&quot;Multiples of 3 or 5&quot;</div></span></a></td>')
_UNSOLVED = ('<td class="tooltip problem_unsolved t_36"><a href="problem=257">257'
             '<span class="tooltiptext_narrow"><div class="strong larger">Problem 257</div>'
             '<div>Solved by 1,060</div><div class="smaller">Difficulty: Level 36 [92%]</div>'
             '<div>&quot;Angular Bisectors&quot;</div></span></a></td>')


class ParseProgressTest(unittest.TestCase):

    def test_solved_cell(self) -> None:
        self.assertEqual(parse_progress(f'<table><tr>{_SOLVED}</tr></table>')[1], {
            'title': 'Multiples of 3 or 5', 'level': 0, 'pct': 1, 'solvers': 864300,
            'solved': True, 'date': 'Thu, 2 Jul 2015, 18:16'})        # UK summer → Amsterdam summer

    def test_page_dates_move_from_uk_time_to_amsterdam_time(self) -> None:
        def page(date: str) -> str | int | bool:
            cell = _SOLVED.replace('Thu, 2 Jul 2015, 17:16', date)
            return parse_progress(f'<table><tr>{cell}</tr></table>')[1]['date']
        self.assertEqual(page('Sun, 11 Jan 2026, 23:30'), 'Mon, 12 Jan 2026, 00:30')   # GMT → CET, a day on
        self.assertEqual(page('Sun, 29 Mar 2026, 01:30'), 'Sun, 29 Mar 2026, 03:30')   # both clocks just went
        self.assertEqual(page('not a date'), 'not a date')                             # kept, not dropped


class SolvedDateTest(unittest.TestCase):

    def test_a_record_date_is_an_amsterdam_time(self) -> None:
        when = parse_solved_date('Tue, 13 Oct 2026, 15:02')
        self.assertEqual(when, datetime(2026, 10, 13, 13, 2, tzinfo=UTC))           # CEST is UTC+2
        self.assertEqual(parse_solved_date(''), None)

    def test_format_converts_an_aware_time_and_round_trips(self) -> None:
        text = format_solved_date(datetime(2026, 8, 2, 13, 2, tzinfo=UTC))
        self.assertEqual(text, 'Sun, 2 Aug 2026, 15:02')                             # unpadded day
        self.assertEqual(parse_solved_date(text), datetime(2026, 8, 2, 13, 2, tzinfo=UTC))

    def test_unsolved_cell_keeps_solver_count(self) -> None:
        record = parse_progress(f'<table><tr>{_UNSOLVED}</tr></table>')[257]
        self.assertEqual((record['solvers'], record['solved'], record['date']), (1060, False, ''))

    def test_missing_solver_line_is_unknown(self) -> None:
        cell = _SOLVED.replace('<div>Solved by 864300</div>', '')
        self.assertEqual(parse_progress(f'<table><tr>{cell}</tr></table>')[1]['solvers'], '')

    def test_wrong_page_is_empty(self) -> None:
        self.assertEqual(parse_progress('<html><body>Sign in</body></html>'), {})


if __name__ == '__main__':
    unittest.main()
