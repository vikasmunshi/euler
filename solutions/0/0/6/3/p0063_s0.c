/* Solution to Euler Problem 63: Powerful Digit Counts. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <math.h>

/* Count digits of a long long */
static int ll_digit_count(long long x) {
    if (x <= 0) return 0;
    int count = 0;
    while (x > 0) {
        count++;
        x /= 10;
    }
    return count;
}

/* Compute i^n using integer arithmetic, returning -1 on overflow */
static long long ipow(long long base, int exp) {
    long long result = 1;
    for (int e = 0; e < exp; e++) {
        if (result > 0 && base > 0 && result > (long long)9e18 / base)
            return -1; /* overflow */
        result *= base;
    }
    return result;
}

long long solve(int argc, char *argv[]) {
    (void)argc;
    (void)argv;

    long long result = 0;
    int n = 1;

    while (1) {
        int solutions_this_n = 0;

        /* All valid bases must be 1..9 (base >= 10 gives b^n >= 10^n, too many digits) */
        for (int b = 1; b <= 9; b++) {
            /* Use log10 to check digit count: floor(n * log10(b)) + 1 == n */
            double log_digits;
            if (b == 1) {
                /* 1^n = 1 always has 1 digit */
                log_digits = 0.0;
            } else {
                log_digits = (double)n * log10((double)b);
            }
            int digits_approx = (int)floor(log_digits) + 1;

            if (digits_approx == n) {
                /* Verify with exact integer arithmetic when possible */
                long long r = ipow((long long)b, n);
                if (r > 0) {
                    /* Exact check */
                    if (ll_digit_count(r) == n) {
                        solutions_this_n++;
                    }
                } else {
                    /* Overflow means the number has more than 18 digits,
                     * which would be far more than n for bases 1-9 in practice.
                     * Trust the log10 estimate. */
                    solutions_this_n++;
                }
            }
        }

        if (solutions_this_n == 0) break;

        result += solutions_this_n;
        n++;
    }

    return result;
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