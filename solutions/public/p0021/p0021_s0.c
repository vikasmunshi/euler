/* Solution to Euler Problem 21: Amicable Numbers. */
#include "runner.h"
#include <math.h>

static long long sum_factors(int n) {
    int n_sqrt = (int)sqrt((double)n);
    long long total = 1;
    for (int i = 2; i <= n_sqrt; i++) {
        if (n % i == 0) {
            total += i + n / i;
        }
    }
    if (n_sqrt * n_sqrt == n) {
        total -= n_sqrt;
    }
    return total;
}

const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int max_num = parse_int(argv[1]);

    long long result = 0;
    for (int x = 2; x <= max_num; x++) {
        long long y = sum_factors(x);
        if (y != x && sum_factors((int)y) == x) {
            result += x;
        }
    }
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(result)); return _answer; }
}
