/* Solution to Euler Problem 38: Pandigital Multiples. */
#include "runner.h"

/* True iff n uses each digit 1-9 exactly once (a 1-to-9 pandigital); O(d) via a frequency array. */
static int is_nine_pandigital(long long n) {
    if (n < 100000000LL || n > 999999999LL)
        return 0;
    int digits[10] = {0};
    while (n) {
        int d = (int)(n % 10);
        if (d == 0 || digits[d] == 1)
            return 0;
        digits[d] = 1;
        n /= 10;
    }
    int sum = 0;
    for (int i = 1; i <= 9; i++) sum += digits[i];
    return sum == 9;
}

/*
 * Bounded brute force: requiring exactly 9 output digits with n > 1 caps x at 4 digits, so a static
 * (n, max_x) table enumerates every viable case. Scanning x downward within each pair (the
 * concatenation grows monotonically with x) makes the first pandigital hit the largest. O(X_max).
 */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    (void)argc; (void)argv;

    /* (n, max_x) pairs as in the Python solution */
    int pairs[8][2] = {
        {2, 9876}, {3, 987}, {4, 98}, {5, 9},
        {6, 9}, {7, 9}, {8, 9}, {9, 9}
    };

    for (int p = 0; p < 8; p++) {
        int n = pairs[p][0];
        int x = pairs[p][1];
        while (x > 0) {
            /* Build the concatenated product x*1 x*2 ... x*n in the string domain, then parse it. */
            char buf[64];
            buf[0] = '\0';
            for (int i = 1; i <= n; i++) {
                char tmp[32];
                snprintf(tmp, sizeof(tmp), "%d", i * x);
                strcat(buf, tmp);
            }
            long long number = atoll(buf);
            if (is_nine_pandigital(number)) {
                { snprintf(_answer, sizeof _answer, "%lld", (long long)(number)); return _answer; }
            }
            x--;
        }
    }
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; } /* No solution found */
}