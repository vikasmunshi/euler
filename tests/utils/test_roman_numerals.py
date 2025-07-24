#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for the Roman Numerals Module

This module contains unit tests for the Roman numeral conversion utilities
defined in euler.utils.roman_numerals.
"""

import unittest

from euler.utils.roman_numerals import number_as_roman_numeral, roman_to_number


class TestRomanNumerals(unittest.TestCase):
    """Tests for Roman numeral conversion functions."""

    def test_basic_roman_numerals(self):
        """Test conversion of basic Roman numerals to integers."""
        self.assertEqual(roman_to_number('I'), 1)
        self.assertEqual(roman_to_number('V'), 5)
        self.assertEqual(roman_to_number('X'), 10)
        self.assertEqual(roman_to_number('L'), 50)
        self.assertEqual(roman_to_number('C'), 100)
        self.assertEqual(roman_to_number('D'), 500)
        self.assertEqual(roman_to_number('M'), 1000)

    def test_additive_roman_numerals(self):
        """Test conversion of additive Roman numerals to integers."""
        self.assertEqual(roman_to_number('II'), 2)
        self.assertEqual(roman_to_number('III'), 3)
        self.assertEqual(roman_to_number('VI'), 6)
        self.assertEqual(roman_to_number('VII'), 7)
        self.assertEqual(roman_to_number('VIII'), 8)
        self.assertEqual(roman_to_number('XIII'), 13)
        self.assertEqual(roman_to_number('XVII'), 17)
        self.assertEqual(roman_to_number('XXX'), 30)
        self.assertEqual(roman_to_number('MMXXI'), 2021)

    def test_subtractive_roman_numerals(self):
        """Test conversion of Roman numerals with subtractive notation."""
        self.assertEqual(roman_to_number('IV'), 4)
        self.assertEqual(roman_to_number('IX'), 9)
        self.assertEqual(roman_to_number('XL'), 40)
        self.assertEqual(roman_to_number('XC'), 90)
        self.assertEqual(roman_to_number('CD'), 400)
        self.assertEqual(roman_to_number('CM'), 900)
        self.assertEqual(roman_to_number('MCMXCIX'), 1999)

    def test_complex_roman_numerals(self):
        """Test conversion of complex Roman numerals combining multiple notations."""
        self.assertEqual(roman_to_number('MCMLIV'), 1954)  # Subtractive: CM (900), L (50), IV (4)
        self.assertEqual(roman_to_number('MMXIX'), 2019)   # Additive: MM (2000), X (10), IX (9)
        self.assertEqual(roman_to_number('MMCDXLIV'), 2444)  # Mixed: MM (2000), CD (400), XL (40), IV (4)
        self.assertEqual(roman_to_number('MMMCMXCIX'), 3999)  # Largest standard: MMM (3000), CM (900), XC (90), IX (9)

    def test_basic_integers_to_roman(self):
        """Test conversion of basic integers to Roman numerals."""
        self.assertEqual(number_as_roman_numeral(1), 'I')
        self.assertEqual(number_as_roman_numeral(5), 'V')
        self.assertEqual(number_as_roman_numeral(10), 'X')
        self.assertEqual(number_as_roman_numeral(50), 'L')
        self.assertEqual(number_as_roman_numeral(100), 'C')
        self.assertEqual(number_as_roman_numeral(500), 'D')
        self.assertEqual(number_as_roman_numeral(1000), 'M')

    def test_additive_integers_to_roman(self):
        """Test conversion of integers to additive Roman numerals."""
        self.assertEqual(number_as_roman_numeral(2), 'II')
        self.assertEqual(number_as_roman_numeral(3), 'III')
        self.assertEqual(number_as_roman_numeral(6), 'VI')
        self.assertEqual(number_as_roman_numeral(7), 'VII')
        self.assertEqual(number_as_roman_numeral(8), 'VIII')
        self.assertEqual(number_as_roman_numeral(30), 'XXX')
        self.assertEqual(number_as_roman_numeral(300), 'CCC')
        self.assertEqual(number_as_roman_numeral(2000), 'MM')

    def test_subtractive_integers_to_roman(self):
        """Test conversion of integers to Roman numerals with subtractive notation."""
        self.assertEqual(number_as_roman_numeral(4), 'IV')
        self.assertEqual(number_as_roman_numeral(9), 'IX')
        self.assertEqual(number_as_roman_numeral(40), 'XL')
        self.assertEqual(number_as_roman_numeral(90), 'XC')
        self.assertEqual(number_as_roman_numeral(400), 'CD')
        self.assertEqual(number_as_roman_numeral(900), 'CM')

    def test_complex_integers_to_roman(self):
        """Test conversion of complex integers to Roman numerals."""
        self.assertEqual(number_as_roman_numeral(14), 'XIV')
        self.assertEqual(number_as_roman_numeral(19), 'XIX')
        self.assertEqual(number_as_roman_numeral(49), 'XLIX')
        self.assertEqual(number_as_roman_numeral(99), 'XCIX')
        self.assertEqual(number_as_roman_numeral(444), 'CDXLIV')
        self.assertEqual(number_as_roman_numeral(999), 'CMXCIX')
        self.assertEqual(number_as_roman_numeral(1954), 'MCMLIV')
        self.assertEqual(number_as_roman_numeral(1999), 'MCMXCIX')
        self.assertEqual(number_as_roman_numeral(2019), 'MMXIX')
        self.assertEqual(number_as_roman_numeral(2444), 'MMCDXLIV')
        self.assertEqual(number_as_roman_numeral(3999), 'MMMCMXCIX')

    def test_bidirectional_conversion(self):
        """Test that converting to Roman and back gives the original number."""
        numbers = [1, 4, 9, 14, 19, 42, 99, 400, 999, 1954, 1999, 2019, 2444, 3999]
        for number in numbers:
            roman = number_as_roman_numeral(number)
            self.assertEqual(roman_to_number(roman), number,
                             f"Failed bidirectional conversion for {number}")

    def test_year_conversions(self):
        """Test conversion of years to Roman numerals and back."""
        years = {
            1776: 'MDCCLXXVI',  # American Independence
            1789: 'MDCCLXXXIX',  # French Revolution
            1917: 'MCMXVII',     # Russian Revolution
            1945: 'MCMXLV',      # End of WWII
            1969: 'MCMLXIX',     # Moon Landing
            2000: 'MM',          # Millennium
            2023: 'MMXXIII'      # Recent year
        }

        for year, roman in years.items():
            # Test number to Roman
            self.assertEqual(number_as_roman_numeral(year), roman,
                             f"Failed to convert {year} to Roman numeral")
            # Test Roman to number
            self.assertEqual(roman_to_number(roman), year,
                             f"Failed to convert {roman} to number")


if __name__ == '__main__':
    unittest.main()
