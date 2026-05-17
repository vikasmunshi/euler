/* Solution to Euler Problem 78: Coin Partitions. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

long long solve(int argc, char *argv[]) {
    int divisor = atoi(argv[1]);

    /* Allocate a growing array for partition values mod divisor */
    int capacity = 100000;
    long long *partitions = malloc((size_t)capacity * sizeof(long long));
    if (!partitions) {
        fprintf(stderr, "Out of memory\n");
        return -1;
    }
    partitions[0] = 1;  /* p(0) = 1 */

    int n = 1;
    while (1) {
        if (n >= capacity) {
            capacity *= 2;
            long long *tmp = realloc(partitions, (size_t)capacity * sizeof(long long));
            if (!tmp) {
                fprintf(stderr, "Out of memory\n");
                free(partitions);
                return -1;
            }
            partitions = tmp;
        }

        long long pval = 0;
        int k = 1;
        while (1) {
            /* generalized pentagonal numbers: g(k) = k*(3k-1)/2, g(-k) = k*(3k+1)/2 */
            long long pent_pos = (long long)k * (3 * k - 1) / 2;
            long long pent_neg = (long long)k * (3 * k + 1) / 2;

            if (pent_pos > n) break;

            int sign = (k % 2 == 1) ? 1 : -1;

            pval += sign * partitions[n - pent_pos];

            if (pent_neg <= n) {
                pval += sign * partitions[n - pent_neg];
            }

            k++;
        }

        pval = ((pval % divisor) + divisor) % divisor;
        partitions[n] = pval;

        if (pval == 0) {
            free(partitions);
            return (long long)n;
        }

        n++;
    }
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