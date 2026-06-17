/* Solution to Euler Problem 73: Counting Fractions in a Range. */
#include "runner.h"

const char *solve(int argc, char *argv[]) {
    /* Iterative Farey neighbour traversal between 1/3 and 1/2: from the neighbour identity
       bc - ad = 1, the next denominator is d_next = D - ((D + prev_d) mod d). Only denominators
       are tracked (numerators are forced by the boundaries). O(answer) time. */
    static char _answer[32];
    int max_d = parse_int(argv[1]);
    int lower_denominator = 3;
    int upper_denominator = 2;
    /* Largest denominator of the form 2 + 3k not exceeding max_d: the fraction just above 1/3. */
    int d = upper_denominator + lower_denominator * ((max_d - upper_denominator) / lower_denominator);
    int prev_d = lower_denominator;
    long long count = 0;
    /* Walk upward, counting one fraction per step; stop at denominator 2 (the upper bound 1/2). */
    while (d != upper_denominator) {
        count++;
        int new_d = max_d - (max_d + prev_d) % d;
        prev_d = d;
        d = new_d;
    }
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(count)); return _answer; }
}