/* Solution to Euler Problem 14: Longest Collatz Sequence. */
#include "runner.h"

static long long *cache = NULL;
static long long cache_size = 0;

/* Number of terms in the Collatz chain from n down to 1. Values >= cache_size
   (the 3n+1 excursions above the limit) are computed but not cached. */
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

/* Memoised recursion on Collatz chain length; ~O(N log N) for limit N. A flat
   calloc'd array (rebuilt per call, so each benchmarked run pays the full cost)
   caches chain lengths so shared tails are reused. Only the upper half of the
   range is scanned: any x above the largest power of two below the limit
   dominates 2x in the lower half, whose chain is just x's plus one step. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    long long max_number = (argc > 1) ? parse_int(argv[1]) : 1000000LL;

    cache_size = max_number + 1;
    cache = (long long *)calloc((size_t)cache_size, sizeof(long long));
    if (!cache) {
        fprintf(stderr, "Out of memory\n");
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
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

    { snprintf(_answer, sizeof _answer, "%lld", (long long)(starting_number)); return _answer; }
}
