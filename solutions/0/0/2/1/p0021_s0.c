/* Solution to Euler Problem 21: Amicable Numbers. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <time.h>

static long long sum_factors(int n) {
    int n_sqrt = (int)sqrt((double)n);
    long long total = 1;
    for (int i = 2; i <= n_sqrt; i++) {
        if (n % i == 0) {
            total += i + n / i;
        }
    }
    if (n_sqrt * n_sqrt == n) {
        total -= n_sqrt;
    }
    return total;
}

long long solve(int argc, char *argv[]) {
    int max_num = atoi(argv[1]);

    long long result = 0;
    for (int x = 2; x <= max_num; x++) {
        long long y = sum_factors(x);
        if (y != x && sum_factors((int)y) == x) {
            result += x;
        }
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