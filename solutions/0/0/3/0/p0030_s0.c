/* Solution to Euler Problem 30: Digit Fifth Powers. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <time.h>

/* Compute integer power */
static long long ipow(long long base, int exp) {
    long long result = 1;
    for (int i = 0; i < exp; i++) result *= base;
    return result;
}

/* Sum of nth powers of digits of num */
static long long digit_power_sum(long long num, int n) {
    long long s = 0;
    while (num > 0) {
        int d = (int)(num % 10);
        s += ipow(d, n);
        num /= 10;
    }
    return s;
}

long long solve(int argc, char *argv[]) {
    int n = atoi(argv[1]);

    /* upper_bound_num_digits = ceil(log(n * 9^n, 10)) */
    double max_sum = (double)n * pow(9.0, (double)n);
    int upper_bound_num_digits = (int)ceil(log10(max_sum));

    int k = upper_bound_num_digits;

    /* Enumerate combinations_with_replacement(range(10), k)
     * using indices[0..k-1] each in [0..9], non-decreasing */
    int *indices = calloc((size_t)k, sizeof(int));
    if (!indices) return -1;

    long long total = 0;

    /* Iterate over all non-decreasing sequences of length k from {0,...,9} */
    while (1) {
        /* Compute sum of nth powers of current multiset */
        long long num = 0;
        for (int i = 0; i < k; i++) {
            num += ipow(indices[i], n);
        }

        /* Check: num > 9 and digit_power_sum(num) == num */
        if (num > 9 && digit_power_sum(num, n) == num) {
            total += num;
        }

        /* Advance to next combination with replacement */
        int pos = k - 1;
        while (pos >= 0 && indices[pos] == 9) {
            pos--;
        }
        if (pos < 0) break;
        int val = indices[pos] + 1;
        for (int i = pos; i < k; i++) {
            indices[i] = val;
        }
    }

    free(indices);
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