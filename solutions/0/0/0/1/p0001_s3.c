/* Solution to Euler Problem 1: Multiples of 3 or 5. */
#include "runner.h"

/* Sum of the arithmetic series 0, d, 2d, ... below max_limit. */
static long long sum_arithmetic_series_range(int common_difference, long long max_limit) {
    long long total = 0;
    for (long long term = 0; term < max_limit; term += common_difference) {
        total += term;
    }
    return total;
}

/* Multiples of 3 or 5 below the limit by inclusion-exclusion (3 + 5 - 15),
 * summing each arithmetic series. O(limit). */
const char *solve(int argc, char *argv[]) {
    long long max_limit = parse_int(argv[1]);
    long long result = sum_arithmetic_series_range(3, max_limit)
                     + sum_arithmetic_series_range(5, max_limit)
                     - sum_arithmetic_series_range(15, max_limit);
    static char answer[32];
    snprintf(answer, sizeof answer, "%lld", result);
    return answer;
}
