/* Solution to Euler Problem 16: Power Digit Sum. */
#include "runner.h"

/* No native big integers in C: hold base**power as a little-endian array of
 * decimal digits (least-significant at index 0) and build it by multiplying by
 * base `power` times (schoolbook long multiplication), then sum the digits.
 * O(power * digits) = O(power^2). */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int base  = parse_int(argv[1]);
    int power = parse_int(argv[2]);

    /* We'll store the big number in a decimal digit array.
     * 2^10000 has at most ceil(10000 * log10(2)) + 1 ~ 3011 decimal digits.
     * Allocate generously. */
    int max_digits = (int)(power * 0.30103 + 10) + 10;
    unsigned char *digits = calloc((size_t)max_digits, sizeof(unsigned char));
    if (!digits) {
        fprintf(stderr, "Out of memory\n");
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }

    /* Start with 1 */
    digits[0] = 1;
    int len = 1;

    /* Repeatedly multiply by base, power times */
    for (int i = 0; i < power; i++) {
        int carry = 0;
        for (int j = 0; j < len; j++) {
            int val = digits[j] * base + carry;
            digits[j] = (unsigned char)(val % 10);
            carry = val / 10;
        }
        while (carry > 0) {
            digits[len++] = (unsigned char)(carry % 10);
            carry /= 10;
        }
    }

    long long sum = 0;
    for (int i = 0; i < len; i++) {
        sum += digits[i];
    }

    free(digits);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(sum)); return _answer; }
}
