/* Solution to Euler Problem 1: Multiples of 3 or 5. */
#include "runner.h"

/* Closed-form sum of 0, d, 2d, ... below max_limit: d*n(n+1)/2. */
static long long sum_arithmetic_series(int common_difference, long long max_limit) {
    long long n = (max_limit - 1) / common_difference;
    return (long long)common_difference * (n * (n + 1)) / 2;
}

/* Multiples of 3 or 5 below the limit by inclusion-exclusion (3 + 5 - 15),
 * each part from the closed-form arithmetic series. O(1). */
const char *solve(int argc, char *argv[]) {
    long long max_limit = parse_int(argv[1]);
    long long result = sum_arithmetic_series(3, max_limit)
                     + sum_arithmetic_series(5, max_limit)
                     - sum_arithmetic_series(15, max_limit);
    static char answer[32];
    snprintf(answer, sizeof answer, "%lld", result);
    return answer;
}
