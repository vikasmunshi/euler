/* Solution to Euler Problem 69: Totient Maximum. */
#include "runner.h"

/*
 * Greedy primorial accumulation: n/phi(n) = product over distinct primes p of p/(p-1),
 * so the maximiser under a bound is the product of the smallest consecutive primes (a
 * primorial) that stays within the limit. Multiply successive primes (found by trial
 * division) into the running product, committing each only while it stays <= limit.
 * Fewer than ~15 primes suffice since 2*3*5*7*11*13*17*19*23 already exceeds 1,000,000,
 * so this is effectively O(1).
 */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    long long limit = parse_int(argv[1]);

    long long result = 1;

    int candidate = 2;
    while (1) {
        /* Trial-division primality test: check odd divisors up to sqrt(candidate). */
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
            /* Validate before committing: only adopt the larger product if it fits the limit. */
            long long next = result * candidate;
            if (next > limit) {
                break;
            }
            result = next;
        }

        candidate = (candidate == 2) ? 3 : candidate + 2;
    }

    { snprintf(_answer, sizeof _answer, "%lld", (long long)(result)); return _answer; }
}