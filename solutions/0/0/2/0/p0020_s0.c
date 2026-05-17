/* Solution to Euler Problem 20: Factorial Digit Sum. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

/* Big integer stored as array of decimal digits (little-endian: digits[0] is least significant) */
#define MAX_DIGITS 512

long long solve(int argc, char *argv[]) {
    int n = (argc >= 2) ? atoi(argv[1]) : 100;

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

    return digit_sum;
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