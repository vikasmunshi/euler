/* Solution to Euler Problem 9: Special Pythagorean Triplet. */
#include "runner.h"

const char *solve(int argc, char *argv[]) {
    /* Bounded two-variable search: the linear constraint fixes c = S - a - b, so only
       a (1..S/4) and b (a..S/2) are searched; return a*b*c on the first Pythagorean hit. O(S^2). */
    static char _answer[32];
    int sum_sides = parse_int(argv[1]);

    for (int a = 1; a < sum_sides / 4 + 1; a++) {
        for (int b = a; b < sum_sides / 2; b++) {
            int c = sum_sides - a - b;
            if (a * a + b * b == c * c) {
                { snprintf(_answer, sizeof _answer, "%lld", (long long)((long long)a * b * c)); return _answer; }
            }
        }
    }

    fprintf(stderr, "No Pythagorean triplet exists with sum %d\n", sum_sides);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
}
