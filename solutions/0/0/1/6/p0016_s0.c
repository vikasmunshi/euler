/* Solution to Euler Problem 16: Power Digit Sum. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

long long solve(int argc, char *argv[]) {
    int base  = atoi(argv[1]);
    int power = atoi(argv[2]);

    /* We'll store the big number in a decimal digit array.
     * 2^10000 has at most ceil(10000 * log10(2)) + 1 ~ 3011 decimal digits.
     * Allocate generously. */
    int max_digits = (int)(power * 0.30103 + 10) + 10;
    unsigned char *digits = calloc((size_t)max_digits, sizeof(unsigned char));
    if (!digits) {
        fprintf(stderr, "Out of memory\n");
        return -1;
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
    return sum;
}

/* Usage: ./file <base> <power> [--runs=1] [--show]
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