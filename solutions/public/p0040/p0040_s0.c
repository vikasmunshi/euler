/* Solution to Euler Problem 40: Champernowne's Constant. */
#include "runner.h"
#include <math.h>

/* Locate digit n by walking d-digit bands (length d*9*10^(d-1)), then floor-div/mod; O(log n). */
static int get_nth_digit_champernowne(long long n) {
    long long length_till_num_digits = 0;
    long long length_with_num_digits = 0;
    int num_digits = 0;

    while (length_with_num_digits < n) {
        num_digits++;
        length_till_num_digits = length_with_num_digits;
        /* Band length num_digits * 9 * 10^(num_digits-1) via exact integer multiplication. */
        long long band = (long long)num_digits * 9;
        for (int k = 0; k < num_digits - 1; k++) band *= 10;
        length_with_num_digits += band;
    }

    long long offset_of_number = n - length_till_num_digits - 1;
    long long digit_in_number = offset_of_number % num_digits;
    /* First number in this band is 10^(num_digits-1); add the within-band index. */
    long long number = 1;
    for (int k = 0; k < num_digits - 1; k++) number *= 10;
    number += offset_of_number / num_digits;

    /* Extract the digit_in_number-th digit by formatting into a buffer and subtracting '0'. */
    char buf[32];
    snprintf(buf, sizeof(buf), "%lld", number);
    return buf[digit_in_number] - '0';
}

/* Fold the product of band-walk lookups at positions 10^0..10^i; O(i log(10^i)) integer ops. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int i = parse_int(argv[1]);

    long long product = 1;
    long long pos = 1;
    for (int k = 0; k <= i; k++) {
        int d = get_nth_digit_champernowne(pos);
        product *= d;
        pos *= 10;
    }
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(product)); return _answer; }
}