/* Solution to Euler Problem 97: Large Non-Mersenne Prime. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static long long mod_pow(long long base, long long exp, long long mod) {
    long long result = 1LL;
    base %= mod;
    while (exp > 0) {
        if (exp & 1LL) {
            result = (long long)((__int128)result * base % mod);
        }
        base = (long long)((__int128)base * base % mod);
        exp >>= 1;
    }
    return result;
}

long long solve(int argc, char *argv[]) {
    /* argv[1] = num_digits
     * argv[2..] = tokens of the prime expression
     * Concatenate all tokens after argv[1] into one string, then parse. */
    int num_digits = atoi(argv[1]);

    long long divisor = 1LL;
    for (int i = 0; i < num_digits; i++) {
        divisor *= 10LL;
    }

    /* Build full expression string from remaining args */
    char expr[256];
    expr[0] = '\0';
    for (int i = 2; i < argc; i++) {
        if (i > 2) strcat(expr, " ");
        strcat(expr, argv[i]);
    }

    /* Parse coefficient: first token (digits at start) */
    long long coefficient = atoll(expr);

    /* Find '^' in the expression to get exponent */
    char *caret = strchr(expr, '^');
    long long exponent = 0LL;
    if (caret != NULL) {
        exponent = atoll(caret + 1);
    }

    /* result = (coefficient * 2^exponent + 1) mod divisor */
    long long power = mod_pow(2LL, exponent, divisor);
    long long result = (long long)((__int128)(coefficient % divisor) * power % divisor);
    result = (result + 1LL) % divisor;
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