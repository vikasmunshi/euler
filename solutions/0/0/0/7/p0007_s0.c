/* Solution to Euler Problem 7: 10 001st Prime. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <time.h>

long long solve(int argc, char *argv[]) {
    int n = atoi(argv[1]);

    if (n == 1) return 2;

    int max_expected_value = (int)(n * log((double)n));

    int *numbers = (int *)malloc((size_t)(max_expected_value + 1) * sizeof(int));
    if (!numbers) {
        fprintf(stderr, "Out of memory\n");
        return -1;
    }
    for (int k = 0; k <= max_expected_value; k++) {
        numbers[k] = k;
    }

    for (int i = 1; i <= max_expected_value; i++) {
        if (numbers[i] == 0) continue;
        for (int j = i; ; j++) {
            long long idx = (long long)i + j + 2LL * i * j;
            if (idx > max_expected_value) break;
            numbers[idx] = 0;
        }
    }

    /* Collect non-zero indices and pick (n-2)-th (0-indexed), then convert to odd number */
    /* We need the (n-2)-th surviving index (skipping index 0 which maps to odd 1) */
    /* numbers[0] = 0 already, so we count non-zero entries from index 1 onward */
    int count = 0;
    long long result = -1;
    for (int k = 1; k <= max_expected_value; k++) {
        if (numbers[k] != 0) {
            if (count == n - 2) {
                result = 2LL * k + 1;
                break;
            }
            count++;
        }
    }

    free(numbers);
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