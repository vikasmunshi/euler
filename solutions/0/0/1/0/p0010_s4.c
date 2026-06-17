/* Solution to Euler Problem 10: Summation of Primes. */
#include "runner.h"
#include <primesieve.h>

/* Sum primes below max_num via the primesieve library's optimised wheel-factorised sieve; ~O(n). */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int max_num = parse_int(argv[1]);
    if (max_num < 2) { snprintf(_answer, sizeof _answer, "%lld", (long long)(0)); return _answer; }
    /* Sum of primes in [2, max_num - 1] */
    size_t size = 0;
    uint64_t *primes = (uint64_t *)primesieve_generate_primes(
        2, (uint64_t)(max_num - 1), &size, UINT64_PRIMES);
    if (!primes) { snprintf(_answer, sizeof _answer, "%lld", (long long)(0)); return _answer; }

    long long sum = 0;
    for (size_t i = 0; i < size; i++) {
        sum += (long long)primes[i];
    }
    primesieve_free(primes);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(sum)); return _answer; }
}
