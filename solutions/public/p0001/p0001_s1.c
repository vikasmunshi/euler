/* Solution to Euler Problem 1: Multiples of 3 or 5. */
#include "runner.h"

/* Multiples of 3 or 5 below the limit by scanning every term and testing
 * divisibility. O(limit). */
const char *solve(int argc, char *argv[]) {
    long long max_limit = parse_int(argv[1]);
    long long result = 0;
    for (long long term = 0; term < max_limit; term++) {
        if (term % 3 == 0 || term % 5 == 0) {
            result += term;
        }
    }
    static char answer[32];
    snprintf(answer, sizeof answer, "%lld", result);
    return answer;
}
