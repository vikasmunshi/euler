/* Solution to Euler Problem 46: Goldbach's Other Conjecture. */
#include "runner.h"
#include <math.h>

/* Enumerate integers; decide primality by trial division against the known primes up to sqrt(n),
 * then for each odd composite test n = p + 2k^2 over those primes, returning the first that fails.
 * Per-candidate cost O(pi(n)), so O(N^2 / ln N) overall - the same approach as the Python sibling. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    (void)argc; (void)argv;

    /* Known primes in a doubling dynamic array (amortised O(1) insertion). */
    int primes_cap = 1024;
    int primes_count = 0;
    int *primes = malloc((size_t)primes_cap * sizeof(int));
    if (!primes) { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }

    long long answer = -1;
    int current = 2;

    while (1) {
        /* Primality by trial division: any composite has a prime factor no larger than its sqrt. */
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
            /* Record the prime, doubling capacity when the buffer is full. */
            if (primes_count >= primes_cap) {
                primes_cap *= 2;
                primes = realloc(primes, (size_t)primes_cap * sizeof(int));
                if (!primes) { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
            }
            primes[primes_count++] = current;
        } else {
            /* Composite: only odd composites are candidates for the conjecture. */
            if (current % 2 != 0) {
                /* Seek a prime p (p != 2) with (current - p) / 2 a perfect square; the first odd
                 * composite admitting no such p is the counterexample we want. */
                int found = 0;
                for (int i = 0; i < primes_count; i++) {
                    int p = primes[i];
                    if (p == 2) continue;
                    if (p >= current) break;
                    int diff = current - p;
                    if (diff <= 0) break;
                    /* diff must be even for (current - p) / 2 to be an integer. */
                    if (diff % 2 != 0) continue;
                    int half = diff / 2;
                    /* Exact perfect-square test: floating sqrt then integer multiply-and-compare. */
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
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(answer)); return _answer; }
}