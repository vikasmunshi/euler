/* Solution to Euler Problem 100: Arranged Probability. */
#include "runner.h"

/* Solve the Pell equation x^2 - 2*y^2 = -1 by iterating its linear recurrence; O(log total).
   The condition P(BB) = 1/2 rearranges to (2n-1)^2 - 2*(2b-1)^2 = -1 with x = 2n-1, y = 2b-1.
   From (1, 1) each next solution is (x, y) -> (3x + 4y, 2x + 3y); x and y stay odd so n and b
   recover exactly, and solutions grow geometrically so ~40 steps reach 10^12. Values fit in
   64-bit signed, so long long suffices without big-integer machinery. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    long long total_discs = parse_int(argv[1]);
    long long x = 1, y = 1;
    while (1) {
        /* Use temporaries so the new x does not clobber the old x before y is computed. */
        long long nx = 3 * x + 4 * y;
        long long ny = 2 * x + 3 * y;
        x = nx;
        y = ny;
        long long n = (x + 1) / 2;
        long long b = (y + 1) / 2;
        if (n >= total_discs) {
            { snprintf(_answer, sizeof _answer, "%lld", (long long)(b)); return _answer; }
        }
    }
}