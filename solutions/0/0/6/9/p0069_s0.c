/* Solution to Euler Problem 69: Totient Maximum. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

long long solve(int argc, char *argv[]) {
    long long limit = atoll(argv[1]);

    /* Greedy primorial accumulation: multiply successive primes until exceeding limit */
    /* We only need a small number of primes, so use a simple trial approach */
    long long result = 1;

    /* Generate primes and multiply them in */
    /* We need at most ~15 primes since 2*3*5*7*11*13*17*19*23 > 1,000,000 */
    int candidate = 2;
    while (1) {
        /* Check if candidate is prime */
        int is_prime = 1;
        if (candidate > 2 && candidate % 2 == 0) {
            is_prime = 0;
        } else {
            for (int d = 3; (long long)d * d <= candidate; d += 2) {
                if (candidate % d == 0) {
                    is_prime = 0;
                    break;
                }
            }
        }

        if (is_prime) {
            long long next = result * candidate;
            if (next > limit) {
                break;
            }
            result = next;
        }

        candidate = (candidate == 2) ? 3 : candidate + 2;
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