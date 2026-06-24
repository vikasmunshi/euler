/* Solution to Euler Problem 1: Multiples of 3 or 5. */
#include "runner.h"

/* Sum of range(start, stop, step), accumulated by iteration. */
static long long sum_range(long long start, long long stop, long long step) {
    /* Mirror CPython's sum(range(start, stop, step)): accumulate by iteration,
       not the closed-form formula (that is index 0's distinct approach). */
    long long total = 0;
    for (long long term = start; term < stop; term += step) {
        total += term;
    }
    return total;
}

/* Multiples of 3 or 5 below the limit by inclusion-exclusion (3 + 5 - 15),
 * each part summed over its range. O(limit). */
const char *solve(int argc, char *argv[]) {
    long long max_limit = parse_int(argv[1]);
    long long result = sum_range(0, max_limit, 3)
                     + sum_range(0, max_limit, 5)
                     - sum_range(0, max_limit, 15);
    static char answer[32];
    snprintf(answer, sizeof answer, "%lld", result);
    return answer;
}
