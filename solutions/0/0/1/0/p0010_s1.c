/* Solution to Euler Problem 10: Summation of Primes. */
#include "runner.h"

/* Sum the primes up to max_num with the Sieve of Sundaram; O(n log n) time, O(n) space. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int max_num = parse_int(argv[1]);
    if (max_num < 2) { snprintf(_answer, sizeof _answer, "%lld", (long long)(0)); return _answer; }

    long long n = (max_num - 1) / 2;

    unsigned char *marked = calloc((size_t)(n + 1), 1);
    if (!marked) { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }

    for (long long i = 1; i <= n; i++) {
        long long j = i;
        while (i + j + 2 * i * j <= n) {
            marked[i + j + 2 * i * j] = 1;
            j++;
        }
    }

    long long sum = (max_num >= 2) ? 2 : 0;
    for (long long i = 1; i <= n; i++) {
        if (!marked[i]) {
            sum += 2 * i + 1;
        }
    }

    free(marked);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(sum)); return _answer; }
}
