/* Solution to Euler Problem 94: Almost Equilateral Triangles. */
#include "runner.h"

/* Generate valid perimeters via the Pell recurrence x^2 - 3 y^2 = 1; O(log N).
   The integral-area condition reduces to a Pell-type equation with a linear recurrence;
   both triangle families (third side a+1 and a-1) interleave into one increasing
   sequence using the sign alternator m, so terms grow ~4x per step. long long avoids
   overflow since the running sum can exceed a one-billion perimeter past 2^31. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    long long max_perimeter = parse_int(argv[1]);
    long long s = 0, s1 = 1, s2 = 1, m = 1, p = 0;
    while (p <= max_perimeter) {
        /* Compute dependent values into temporaries before write-back (simultaneous update). */
        long long new_s2 = 4 * s2 - s1 + 2 * m;
        long long new_m = -m;
        s = s + p;
        s1 = s2;
        s2 = new_s2;
        m = new_m;
        p = 3 * s2 - m;
    }
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(s)); return _answer; }
}