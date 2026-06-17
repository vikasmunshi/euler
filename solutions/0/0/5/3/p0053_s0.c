/* Solution to Euler Problem 53: Combinatoric Selections. */
#include "runner.h"

const char *solve(int argc, char *argv[]) {
    /*
     * Count binomial coefficients C(n, r) above the threshold by walking each Pascal row with the
     * recurrence C(n, r+1) = C(n, r) * (n - r) / (r + 1). Each row is unimodal and symmetric, so the
     * first r whose coefficient exceeds the threshold makes every entry from r to n-r qualify; add
     * n - 2*r + 1 and stop. O(max_n^2) worst case, far less with the early exit. The long long
     * accumulator carries intermediate coefficients without overflow for n up to 100.
     */
    static char _answer[32];
    int max_n = parse_int(argv[1]);
    long long threshold = parse_int(argv[2]);

    long long count = 0;
    for (int n = 1; n <= max_n; n++) {
        long long c = 1;
        for (int r = 0; r <= n / 2; r++) {
            if (c > threshold) {
                count += n - 2 * r + 1;
                break;
            } else {
                c = c * (n - r) / (r + 1);
            }
        }
    }
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(count)); return _answer; }
}