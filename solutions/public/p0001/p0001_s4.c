/* Solution to Euler Problem 1: Multiples of 3 or 5. */
#include "runner.h"

/* Sum of 0, d, 2d, ... below max_limit, advancing a running term. */
static long long sum_arithmetic_series_loop(int common_difference, long long max_limit) {
    long long total = 0;
    long long term = 0;
    while (term < max_limit) {
        total += term;
        term += common_difference;
    }
    return total;
}

/* Multiples of 3 or 5 below the limit by inclusion-exclusion (3 + 5 - 15),
 * each series summed by an advancing-term loop. O(limit). */
const char *solve(int argc, char *argv[]) {
    long long max_limit = parse_int(argv[1]);
    long long result = sum_arithmetic_series_loop(3, max_limit)
                     + sum_arithmetic_series_loop(5, max_limit)
                     - sum_arithmetic_series_loop(15, max_limit);
    static char answer[32];
    snprintf(answer, sizeof answer, "%lld", result);
    return answer;
}
