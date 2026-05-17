/* Solution to Euler Problem 34: Digit Factorials. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static int factorial[10] = {1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880};

static int digit_factorial_sum(int n) {
    int sum = 0;
    while (n > 0) {
        sum += factorial[n % 10];
        n /= 10;
    }
    return sum;
}

static int num_digits(int n) {
    if (n == 0) return 1;
    int count = 0;
    while (n > 0) { count++; n /= 10; }
    return count;
}

/* Check that all digits in combo (sorted array of length k) appear in num_str */
static int combo_subset_of_num(int *combo, int k, const char *num_str) {
    /* For each digit in combo, check it appears in num_str enough times */
    /* Count occurrences needed from combo, count available in num_str */
    int need[10] = {0};
    for (int i = 0; i < k; i++) need[combo[i]]++;
    int have[10] = {0};
    for (int i = 0; num_str[i]; i++) have[num_str[i] - '0']++;
    for (int d = 0; d < 10; d++) {
        if (need[d] > have[d]) return 0;
    }
    return 1;
}

long long solve(int argc, char *argv[]) {
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

            /* Check: fac_sum has exactly k digits */
            if (num_digits(fac_sum) == k) {
                /* Check: all digits in combo appear in fac_sum */
                char num_str[16];
                snprintf(num_str, sizeof(num_str), "%d", fac_sum);

                if (combo_subset_of_num(combo, k, num_str)) {
                    /* Final check: fac_sum equals sum of factorials of its own digits */
                    if (fac_sum == digit_factorial_sum(fac_sum)) {
                        total += fac_sum;
                    }
                }
            }

            /* Advance combination with replacement (non-decreasing sequences) */
            int pos = k - 1;
            while (pos >= 0 && combo[pos] == 9) pos--;
            if (pos < 0) break;
            int val = combo[pos] + 1;
            for (int i = pos; i < k; i++) combo[i] = val;
        }
    }

    return total;
}

/* Usage: ./file <kwarg>... [--runs=1] [--show]
 * Output: "<runs> <avg_seconds> <result>" */
int main(int argc, char *argv[]) {
    int runs = 1;

    char **solve_argv = malloc((size_t)argc * sizeof(char *));
    if (!solve_argv) {
        fprintf(stderr, "runner: out of memory\n");
        return 1;
    }
    int solve_argc = 0;
    solve_argv[solve_argc++] = argv[0];

    for (int i = 1; i < argc; i++) {
        if (argv[i][0] == '\0') continue;
        if (strncmp(argv[i], "--runs=", 7) == 0) {
            int r = atoi(argv[i] + 7);
            if (r >= 1) runs = r;
            continue;
        }
        if (strcmp(argv[i], "--show") == 0) continue;
        solve_argv[solve_argc++] = argv[i];
    }

    long long result = 0;
    double total = 0.0;
    int rc = 0;
    int has_result = 0;

    for (int r = 0; r < runs; r++) {
        struct timespec t0, t1;
        clock_gettime(CLOCK_MONOTONIC, &t0);
        long long cur = solve(solve_argc, solve_argv);
        clock_gettime(CLOCK_MONOTONIC, &t1);
        total += (double)(t1.tv_sec - t0.tv_sec)
               + (double)(t1.tv_nsec - t0.tv_nsec) * 1e-9;
        if (has_result && cur != result) {
            fprintf(stderr, "Expected consistent result, got %lld previous result=%lld\n",
                    cur, result);
            rc = 1;
        }
        result = cur;
        has_result = 1;
    }

    free(solve_argv);
    printf("%d %.17g %lld\n", runs, total / (double)runs, result);
    return rc;
}