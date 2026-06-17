/* Solution to Euler Problem 6: Sum Square Difference. */
#include "runner.h"

const char *solve(int argc, char *argv[]) {
    /* Closed form: triangular-number square minus square-pyramidal sum, S(n)^2 - SS(n); O(1). */
    static char _answer[32];
    long long n = parse_int(argv[1]);
    long long sum = n * (n + 1) / 2;
    long long square_of_sum = sum * sum;
    long long sum_of_squares = (2 * n + 1) * (n + 1) * n / 6;
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(square_of_sum - sum_of_squares)); return _answer; }
}
