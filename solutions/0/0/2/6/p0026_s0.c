/* Solution to Euler Problem 26: Reciprocal Cycles. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static int gcd(int a, int b) {
    while (b) {
        int t = b;
        b = a % b;
        a = t;
    }
    return a;
}

static int multiplicative_order(int a, int modulus) {
    long long r = 1;
    for (int k = 1; k < modulus; k++) {
        r = r * a % modulus;
        if (r == 1)
            return k;
    }
    return -1; /* no order found */
}

long long solve(int argc, char *argv[]) {
    int limit = atoi(argv[1]);

    int best_len = -1;
    int best_d = -1;

    /* Mirror Python: range(max(limit // 10, 10)) iterations */
    int iters = limit / 10;
    if (iters < 10) iters = 10;

    for (int i = 0; i < iters; i++) {
        int d = limit - i;
        if (d <= 6) continue;
        if (gcd(d, 10) != 1) continue;
        int order = multiplicative_order(10, d);
        if (order < 0) continue;
        if (order > best_len || (order == best_len && d > best_d)) {
            best_len = order;
            best_d = d;
        }
    }

    return (long long)best_d;
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