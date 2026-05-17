/* Solution to Euler Problem 23: Non-Abundant Sums. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static long long sum_proper_divisors(int n) {
    if (n <= 1) return 0;
    long long result = 1;
    for (int i = 2; (long long)i * i <= n; i++) {
        if (n % i == 0) {
            result += i;
            if (i != n / i) {
                result += n / i;
            }
        }
    }
    return result;
}

long long solve(int argc, char *argv[]) {
    (void)argc; (void)argv;
    int limit = 28123;

    /* Collect abundant numbers using trial division */
    int *abundant = malloc((size_t)(limit + 1) * sizeof(int));
    if (!abundant) return -1;
    int abundant_count = 0;

    for (int i = 12; i <= limit; i++) {
        if (sum_proper_divisors(i) > i) {
            abundant[abundant_count++] = i;
        }
    }

    /* Mark all sums of two abundant numbers */
    char *is_abundant_sum = calloc((size_t)(limit + 1), sizeof(char));
    if (!is_abundant_sum) { free(abundant); return -1; }

    for (int i = 0; i < abundant_count; i++) {
        for (int j = i; j < abundant_count; j++) {
            int s = abundant[i] + abundant[j];
            if (s > limit) break;
            is_abundant_sum[s] = 1;
        }
    }
    free(abundant);

    /* Sum all numbers that cannot be written as sum of two abundant numbers */
    long long result = 0;
    for (int i = 1; i <= limit; i++) {
        if (!is_abundant_sum[i]) {
            result += i;
        }
    }
    free(is_abundant_sum);

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