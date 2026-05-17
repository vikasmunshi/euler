/* Solution to Euler Problem 46: Goldbach's Other Conjecture. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <time.h>

long long solve(int argc, char *argv[]) {
    (void)argc; (void)argv;

    /* We'll store known primes in a dynamic array */
    int primes_cap = 1024;
    int primes_count = 0;
    int *primes = malloc((size_t)primes_cap * sizeof(int));
    if (!primes) return -1;

    /*
     * Incremental sieve: use a simple is_prime boolean array up to some limit.
     * Since the answer is 5777, we can use a straightforward approach:
     * iterate over numbers, maintain a list of primes found so far,
     * and for each odd composite, check the Goldbach conjecture.
     */

    /* We'll use a sieve-like approach but simpler:
     * For each number, check primality by trial division against known primes,
     * then test the conjecture for odd composites. */

    long long answer = -1;
    int current = 2;

    while (1) {
        /* Check if current is prime by trial division against known primes */
        int is_prime = 1;
        int sq = (int)sqrt((double)current);
        for (int i = 0; i < primes_count; i++) {
            if (primes[i] > sq) break;
            if (current % primes[i] == 0) {
                is_prime = 0;
                break;
            }
        }

        if (is_prime) {
            /* Add to primes list */
            if (primes_count >= primes_cap) {
                primes_cap *= 2;
                primes = realloc(primes, (size_t)primes_cap * sizeof(int));
                if (!primes) return -1;
            }
            primes[primes_count++] = current;
        } else {
            /* It's composite; check if odd */
            if (current % 2 != 0) {
                /* Check Goldbach's other conjecture:
                 * current = p + 2*k^2 for some prime p < current (p != 2) and integer k >= 1
                 * i.e., (current - p) / 2 must be a perfect square */
                int found = 0;
                for (int i = 0; i < primes_count; i++) {
                    int p = primes[i];
                    if (p == 2) continue;
                    if (p >= current) break;
                    int diff = current - p;
                    if (diff <= 0) break;
                    /* diff must be even */
                    if (diff % 2 != 0) continue;
                    int half = diff / 2;
                    int root = (int)sqrt((double)half);
                    if (root * root == half) {
                        found = 1;
                        break;
                    }
                }
                if (!found) {
                    answer = current;
                    break;
                }
            }
        }

        current++;
    }

    free(primes);
    return answer;
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