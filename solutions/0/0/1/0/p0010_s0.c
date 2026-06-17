/* Solution to Euler Problem 10: Summation of Primes. */
#include "runner.h"
#include <math.h>

/* Sum the primes up to max_num with a Sieve of Eratosthenes; O(n log log n) time, O(n) space. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int max_num = parse_int(argv[1]);
    if (max_num < 2) { snprintf(_answer, sizeof _answer, "%lld", (long long)(0)); return _answer; }

    unsigned char *sieve = calloc((size_t)(max_num + 1), 1);
    if (!sieve) { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }

    memset(sieve, 1, (size_t)(max_num + 1));
    sieve[0] = 0;
    sieve[1] = 0;

    int limit = (int)sqrt((double)max_num);
    for (int i = 2; i <= limit; i++) {
        if (sieve[i]) {
            for (int j = i * i; j <= max_num; j += i) {
                sieve[j] = 0;
            }
        }
    }

    long long sum = 0;
    for (int i = 2; i <= max_num; i++) {
        if (sieve[i]) sum += i;
    }

    free(sieve);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(sum)); return _answer; }
}
