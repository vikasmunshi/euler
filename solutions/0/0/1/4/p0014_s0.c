/* Solution to Euler Problem 14: Longest Collatz Sequence. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static long long *cache = NULL;
static long long cache_size = 0;

static long long collatz_length(long long n) {
    if (n == 1) return 1;
    if (n < cache_size && cache[n] != 0) return cache[n];

    long long result;
    if (n % 2 == 0) {
        result = 1 + collatz_length(n / 2);
    } else {
        result = 1 + collatz_length(3 * n + 1);
    }

    if (n < cache_size) {
        cache[n] = result;
    }
    return result;
}

long long solve(int argc, char *argv[]) {
    long long max_number = (argc > 1) ? atoll(argv[1]) : 1000000LL;

    cache_size = max_number + 1;
    cache = (long long *)calloc((size_t)cache_size, sizeof(long long));
    if (!cache) {
        fprintf(stderr, "Out of memory\n");
        return -1;
    }

    /* Find largest power of two strictly below max_number */
    long long power_of_two = 1;
    while (power_of_two * 2 < max_number) {
        power_of_two *= 2;
    }
    /* power_of_two is now the largest power of two < max_number */

    long long max_length = 0, starting_number = 0;
    for (long long x = max_number; x > power_of_two; x--) {
        long long length = collatz_length(x);
        if (length > max_length) {
            max_length = length;
            starting_number = x;
        }
    }

    free(cache);
    cache = NULL;
    cache_size = 0;

    return starting_number;
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