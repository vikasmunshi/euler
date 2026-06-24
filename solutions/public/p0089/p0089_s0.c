/* Solution to Euler Problem 89: Roman Numerals. */
#include "runner.h"



/* Value of a single Roman symbol; the switch compiles to a fast jump table. */
static int char_value(char c) {
    switch (c) {
        case 'I': return 1;
        case 'V': return 5;
        case 'X': return 10;
        case 'L': return 50;
        case 'C': return 100;
        case 'D': return 500;
        case 'M': return 1000;
        default:  return 0;
    }
}

/* Parse a numeral to an integer by scanning right-to-left, subtracting any symbol smaller than the
   one to its right (the subtractive pairs); O(len). */
static int roman_to_number(const char *numeral, int len) {
    int value = 0, last = 0;
    for (int i = len - 1; i >= 0; i--) {
        int n = char_value(numeral[i]);
        if (last > n)
            value -= n;
        else
            value += n;
        last = n;
    }
    return value;
}

/* Denominations and their numerals as parallel arrays, ordered largest-first; the struct-of-arrays
   layout initialises cleanly from static literals and is read in tandem by the greedy encoder. */
static const int numeral_values[] = {
    1000, 900, 800, 700, 600, 500, 400, 300, 200, 100,
    90, 80, 70, 60, 50, 40, 30, 20, 10,
    9, 8, 7, 6, 5, 4, 3, 2, 1
};
static const char *numeral_strings[] = {
    "M", "CM", "DCCC", "DCC", "DC", "D", "CD", "CCC", "CC", "C",
    "XC", "LXXX", "LXX", "LX", "L", "XL", "XXX", "XX", "X",
    "IX", "VIII", "VII", "VI", "V", "IV", "III", "II", "I"
};
static const int numeral_count = 28;

/* Length of the minimal numeral for an integer, via greedy largest-fitting denominations; only the
   length is accumulated since the answer needs counts, not the string itself. O(len). */
static int number_as_roman_numeral_length(int number) {
    int len = 0;
    while (number > 0) {
        for (int i = 0; i < numeral_count; i++) {
            if (numeral_values[i] <= number) {
                len += (int)strlen(numeral_strings[i]);
                number -= numeral_values[i];
                break;
            }
        }
    }
    return len;
}

/* Convert each numeral to an integer and re-encode it minimally, summing the characters saved;
   O(N) over the N input lines, each numeral of bounded length. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <file_url>\n", argv[0]);
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }

    char *text = get_text_file(argv[1]);
    if (!text) { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }

    long long characters_saved = 0;
    char *ptr = text;
    while (*ptr) {
        /* Skip any leading newline/carriage-return characters */
        while (*ptr == '\r' || *ptr == '\n') ptr++;
        if (*ptr == '\0') break;

        /* Find end of line */
        char *end = ptr;
        while (*end && *end != '\r' && *end != '\n') end++;

        int original_len = (int)(end - ptr);
        if (original_len > 0) {
            int number = roman_to_number(ptr, original_len);
            int minimal_len = number_as_roman_numeral_length(number);
            characters_saved += original_len - minimal_len;
        }
        ptr = end;
    }

    free(text);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(characters_saved)); return _answer; }
}
