/* Solution to Euler Problem 44: Pentagon Numbers. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <time.h>

static long long nth_pentagonal(long long n) {
    return n * (3 * n - 1) / 2;
}

static int is_pentagonal(long long m) {
    double disc = 1.0 + 24.0 * (double)m;
    double sq = sqrt(disc);
    double n = (1.0 + sq) / 6.0;
    long long ni = (long long)round(n);
    return (ni > 0) && (nth_pentagonal(ni) == m);
}

long long solve(int argc, char *argv[]) {
    (void)argc; (void)argv;
    for (long long i = 1; ; i++) {
        long long p_i = nth_pentagonal(i);
        for (long long j = i - 1; j >= 1; j--) {
            long long p_j = nth_pentagonal(j);
            long long diff = p_i - p_j;
            long long sum  = p_i + p_j;
            if (is_pentagonal(diff) && is_pentagonal(sum)) {
                return diff;
            }
        }
    }
    return -1;
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