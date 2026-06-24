/* Solution to Euler Problem 45: Triangular, Pentagonal, and Hexagonal. */
#include "runner.h"
#include <math.h>

/* Scan triangular numbers T(n) from a given index, keeping those whose inverse pentagonal and
   triangular discriminants are perfect squares (root == 5 mod 6 and 3 mod 4); O(k) candidates. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    long long n = (argc >= 2) ? parse_int(argv[1]) : 285;

    while (1) {
        n++;
        long long t = n * (n + 1) / 2;

        double s1 = sqrt((double)(1 + 24 * t));
        if (fmod(s1, 6.0) != 5.0) continue;

        double s2 = sqrt((double)(1 + 8 * t));
        if (fmod(s2, 4.0) != 3.0) continue;

        { snprintf(_answer, sizeof _answer, "%lld", (long long)(t)); return _answer; }
    }
}