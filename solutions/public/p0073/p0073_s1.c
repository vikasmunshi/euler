/* Solution to Euler Problem 73: Counting Fractions in a Range. */
#include "runner.h"

static int g_max_d;

/* Stern-Brocot recursive mediant search: the mediant of boundaries with denominators b_lo and
   b_hi has denominator b_lo + b_hi; recurse into both sub-intervals until the sum exceeds D.
   Tracks only denominators. O(answer) time, O(depth) stack. */
static long long recursion(int lower_denominator, int upper_denominator) {
    int mediant = lower_denominator + upper_denominator;
    if (mediant > g_max_d)
        return 0;
    return 1 + recursion(lower_denominator, mediant) + recursion(mediant, upper_denominator);
}

const char *solve(int argc, char *argv[]) {
    /* Count fractions in (1/3, 1/2) by recursive Stern-Brocot mediant search; O(answer). The bound
       is held in the file-scope g_max_d to keep the hot recursive frame small. */
    static char _answer[32];
    g_max_d = parse_int(argv[1]);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(recursion(3, 2))); return _answer; }
}