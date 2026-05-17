/* Solution to Euler Problem 87: Prime Power Triples. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <time.h>

/* Sieve of Sundaram: returns array of primes up to max_num, sets *count */
static int *primes_sundaram_sieve(int max_num, int *count) {
    *count = 0;
    if (max_num < 2) return NULL;

    int n = (max_num - 1) / 2;
    unsigned char *marked = calloc((size_t)(n + 1), 1);
    if (!marked) return NULL;

    for (int i = 1; i <= n; i++) {
        for (int j = i; i + j + 2 * i * j <= n; j++) {
            marked[i + j + 2 * i * j] = 1;
        }
    }

    /* Count primes */
    int cap = 1; /* include 2 */
    for (int i = 1; i <= n; i++) {
        if (!marked[i]) cap++;
    }

    int *primes = malloc((size_t)cap * sizeof(int));
    if (!primes) { free(marked); return NULL; }

    int idx = 0;
    primes[idx++] = 2;
    for (int i = 1; i <= n; i++) {
        if (!marked[i]) primes[idx++] = 2 * i + 1;
    }

    free(marked);
    *count = idx;
    return primes;
}

long long solve(int argc, char *argv[]) {
    long long max_num = (argc >= 2) ? atoll(argv[1]) : 50000000LL;

    int sqrt_max = (int)sqrt((double)max_num);
    int prime_count = 0;
    int *primes = primes_sundaram_sieve(sqrt_max, &prime_count);
    if (!primes) return -1;

    /* Use a bitset for deduplication */
    unsigned char *seen = calloc((size_t)max_num, 1);
    if (!seen) { free(primes); return -1; }

    long long max_quadruple_cube = max_num - 4;   /* smallest square is 2^2=4 */
    long long max_quadruple      = max_quadruple_cube - 8; /* smallest cube is 2^3=8 */

    long long count = 0;

    for (int i4 = 0; i4 < prime_count; i4++) {
        long long quadruple = (long long)primes[i4] * primes[i4] * primes[i4] * primes[i4];
        if (quadruple > max_quadruple) break;

        for (int i3 = 0; i3 < prime_count; i3++) {
            long long cube = (long long)primes[i3] * primes[i3] * primes[i3];
            long long quadruple_cube = quadruple + cube;
            if (quadruple_cube > max_quadruple_cube) break;

            for (int i2 = 0; i2 < prime_count; i2++) {
                long long square = (long long)primes[i2] * primes[i2];
                long long number = quadruple_cube + square;
                if (number >= max_num) break;

                if (!seen[number]) {
                    seen[number] = 1;
                    count++;
                }
            }
        }
    }

    free(seen);
    free(primes);
    return count;
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