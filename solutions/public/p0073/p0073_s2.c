/* Solution to Euler Problem 73: Counting Fractions in a Range. */
#include "runner.h"

/* Rank of n/d in the Farey sequence F_max_d: the count of reduced fractions in [0, 1] with
   denominator at most max_d that do not exceed n/d. Builds data[i] = floor(i*n/d) (all fractions,
   reduced or not), then an additive Mobius sieve subtracts each data[i] from its multiples,
   leaving the exact coprime count per denominator. O(max_d log max_d). */
static long long rank_fn(int max_d, int n, int d) {
    int len_data = max_d + 1;
    long long *data = malloc((size_t)len_data * sizeof(long long));
    if (!data) return -1;

    for (int i = 0; i < len_data; i++) {
        /* Cast to long long before the product to avoid 32-bit overflow when i is large. */
        data[i] = (long long)i * n / d;
    }

    /* Additive sieve (Mobius inversion): strip multiples so data[i] counts only denominator i. */
    for (int i = 1; i < len_data; i++) {
        for (int j = 2 * i; j < len_data; j += i) {
            data[j] -= data[i];
        }
    }

    long long total = 0;
    for (int i = 0; i < len_data; i++) {
        total += data[i];
    }

    free(data);
    return total;
}

const char *solve(int argc, char *argv[]) {
    /* Counting fractions in (1/3, 1/2) is a rank difference: rank(1/2) - rank(1/3) - 1, where the
       -1 drops 1/2 itself. Each rank is an O(max_d log max_d) Mobius sieve. */
    static char _answer[32];
    int max_d = parse_int(argv[1]);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(rank_fn(max_d, 1, 2) - rank_fn(max_d, 1, 3) - 1)); return _answer; }
}