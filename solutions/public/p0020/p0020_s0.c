/* Solution to Euler Problem 20: Factorial Digit Sum. */
#include "runner.h"

/* Big integer stored as array of decimal digits (little-endian: digits[0] is least significant) */
#define MAX_DIGITS 512

const char *solve(int argc, char *argv[]) {
    /* Build n! as a base-10 digit array via schoolbook multiply-by-scalar, then sum the digits;
       O(n) multiplications over O(n log n) digits (Stirling). Mirrors the Python sibling, but
       implements arbitrary precision by hand since C has no native big-integer type. */
    static char _answer[32];
    int n = (argc >= 2) ? parse_int(argv[1]) : 100;

    /* Store factorial as array of decimal digits, little-endian */
    unsigned char digits[MAX_DIGITS];
    memset(digits, 0, sizeof(digits));
    digits[0] = 1;
    int num_digits = 1;

    for (int i = 2; i <= n; i++) {
        int carry = 0;
        for (int j = 0; j < num_digits; j++) {
            int prod = digits[j] * i + carry;
            digits[j] = prod % 10;
            carry = prod / 10;
        }
        while (carry > 0) {
            digits[num_digits++] = carry % 10;
            carry /= 10;
        }
    }

    long long digit_sum = 0;
    for (int i = 0; i < num_digits; i++) {
        digit_sum += digits[i];
    }

    { snprintf(_answer, sizeof _answer, "%lld", (long long)(digit_sum)); return _answer; }
}
