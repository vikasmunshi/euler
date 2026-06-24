/* Solution to Euler Problem 34: Digit Factorials. */
#include "runner.h"

static int factorial[10] = {1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880};

/* Sum of factorials of the decimal digits of n, via modulo/divide arithmetic. */
static int digit_factorial_sum(int n) {
    int sum = 0;
    while (n > 0) {
        sum += factorial[n % 10];
        n /= 10;
    }
    return sum;
}

/* Number of decimal digits in n. */
static int num_digits(int n) {
    if (n == 0) return 1;
    int count = 0;
    while (n > 0) { count++; n /= 10; }
    return count;
}

/* Check that all digits in combo (sorted array of length k) appear in num_str */
static int combo_subset_of_num(int *combo, int k, const char *num_str) {
    /* Multiplicity check: each digit must occur in num_str at least as often as in combo */
    int need[10] = {0};
    for (int i = 0; i < k; i++) need[combo[i]]++;
    int have[10] = {0};
    for (int i = 0; num_str[i]; i++) have[num_str[i] - '0']++;
    for (int d = 0; d < 10; d++) {
        if (need[d] > have[d]) return 0;
    }
    return 1;
}

/* Enumerate digit multisets (order-independent factorial sums) as non-decreasing sequences over
   lengths 2..7, since no candidate exceeds 7 digits; O(sum_k C(k+9, k)) candidate checks. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    (void)argc; (void)argv;

    int upper_bound_num_digits = 8; /* 2..7 inclusive */
    long long total = 0;

    /* Enumerate combinations with replacement of digits 0-9 for each length */
    /* We use an array of indices into "0123456789" */
    for (int num_digits_len = 2; num_digits_len < upper_bound_num_digits; num_digits_len++) {
        /* Generate all combinations with replacement of length num_digits_len from {0..9} */
        int combo[8] = {0}; /* max 7 digits */
        int k = num_digits_len;

        /* Initialize combo to all zeros */
        for (int i = 0; i < k; i++) combo[i] = 0;

        while (1) {
            /* Compute digit factorial sum */
            int fac_sum = 0;
            for (int i = 0; i < k; i++) fac_sum += factorial[combo[i]];

            /* Guard A: fac_sum must have exactly k digits to be a k-digit candidate */
            if (num_digits(fac_sum) == k) {
                /* Guard B: every digit in combo must appear in fac_sum (necessary, not sufficient) */
                char num_str[16];
                snprintf(num_str, sizeof(num_str), "%d", fac_sum);

                if (combo_subset_of_num(combo, k, num_str)) {
                    /* Guard C: definitive test - fac_sum equals its own digit factorial sum */
                    if (fac_sum == digit_factorial_sum(fac_sum)) {
                        total += fac_sum;
                    }
                }
            }

            /* Advance to next non-decreasing sequence: bump rightmost non-9 position, then
               flatten all later positions to that value */
            int pos = k - 1;
            while (pos >= 0 && combo[pos] == 9) pos--;
            if (pos < 0) break;
            int val = combo[pos] + 1;
            for (int i = pos; i < k; i++) combo[i] = val;
        }
    }

    { snprintf(_answer, sizeof _answer, "%lld", (long long)(total)); return _answer; }
}