/* Solution to Euler Problem 86: Cuboid Route. */
#include "runner.h"
#include <math.h>

/*
 * Unfold the cuboid so the shortest surface path becomes the hypotenuse
 * sqrt(a^2 + (b+c)^2) under the canonical ordering a >= b >= c. Fix the largest
 * dimension a and scan s = b+c in [1, 2a], testing a^2 + s^2 for a perfect
 * square once per s, then add the O(1) count of (b, c) pairs summing to s with
 * b <= a. Accumulate monotonically and return a the instant the count crosses
 * the target. O(M^2) where M is the answer.
 */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int target_solutions = parse_int(argv[1]);
    long long result = 0;

    for (int a = 1; ; a++) {
        for (int b_plus_c = 1; b_plus_c <= 2 * a; b_plus_c++) {
            /* Perfect-square test via round(sqrt)-then-square; exact for these magnitudes. */
            double val = (double)a * a + (double)b_plus_c * b_plus_c;
            double sq = sqrt(val);
            long long isq = (long long)(sq + 0.5);
            if (isq * isq == (long long)val) {
                /* Pairs (b, c) with b >= c >= 1, b + c = s and the cap b <= a. */
                int count;
                if (b_plus_c <= a + 1) {
                    /* Cap c >= s - a is not binding, so floor(s/2) pairs. */
                    count = b_plus_c / 2;
                } else {
                    /* Cap binds: floor(s/2) - (s - a) + 1 surviving pairs. */
                    count = (2 * a - b_plus_c + 2) / 2;
                }
                result += count;
                if (result >= target_solutions) {
                    { snprintf(_answer, sizeof _answer, "%lld", (long long)(a)); return _answer; }
                }
            }
        }
    }
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
}