#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Links the content pages rewrite: a statement's links to other projecteuler.net pages, and a
nested topic's relative links to its neighbours (euler_site.site.content)."""
from __future__ import annotations

import unittest

from euler_site.site import content


class StatementLinkTests(unittest.TestCase):
    def test_a_problem_link_goes_to_that_problems_page_here(self) -> None:
        html = content.rewrite_statement_links('<a href="problem=67">Problem 67</a>', 18)
        self.assertIn('href="/solutions/0067/"', html)
        self.assertIn('hx-get="/solutions/0067/"', html)

    def test_another_projecteuler_page_goes_to_projecteuler(self) -> None:
        html = content.rewrite_statement_links('<a href="about=roman_numerals">this</a>', 89)
        self.assertIn('href="https://projecteuler.net/about=roman_numerals"', html)

    def test_resources_are_still_rooted_at_the_problem(self) -> None:
        html = content.rewrite_statement_links('<img src="resources/0096_1.png"><a href="#x">x</a>', 96)
        self.assertIn('src="/solutions/0096/resources/0096_1.png"', html)
        self.assertIn('href="#x"', html)


class NestedTopicLinkTests(unittest.TestCase):
    def render(self, markdown: str) -> str:
        return content.render_markdown(markdown, route_base='/topics/', page_dir='domain')

    def test_a_sibling_resolves_in_the_same_folder(self) -> None:
        self.assertIn('href="/topics/domain/functional-graph"', self.render('[g](functional-graph.md)'))

    def test_a_cousin_resolves_across_folders(self) -> None:
        html = self.render('[m](../technique/memoization.md#top)')
        self.assertIn('href="/topics/technique/memoization#top"', html)

    def test_a_link_out_of_the_tree_is_repo_relative(self) -> None:
        html = self.render('[g](../../docs/user-guide.md)')
        self.assertIn('href="/docs/file/docs/user-guide.md"', html)

    def test_a_flat_tree_is_unchanged(self) -> None:
        html = content.render_markdown('[g](user-guide.md)', route_base='/docs/')
        self.assertIn('href="/docs/user-guide"', html)


if __name__ == '__main__':
    unittest.main()
