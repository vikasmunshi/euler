/* Solution to Euler Problem 64: Odd Period Square Roots. */
#include "runner.h"
#include <math.h>

/* Period of the continued fraction of sqrt(n) via cycle detection on the integer state
   triple (m, d, a) of the quadratic-irrational recurrence; O(period) per call. */
static int get_period_length(int n) {
    int a0 = (int)sqrt((double)n);
    /* Correct the double-based sqrt to the exact integer floor (53-bit mantissa). */
    while ((long long)(a0 + 1) * (a0 + 1) <= n) a0++;
    while ((long long)a0 * a0 > n) a0--;

    int a = a0;
    int d = 1, m = 0;
    int period = 0;

    /* Growable buffer of visited (m, d, a) triples; doubles via realloc on overflow. */
    int capacity = 64;
    int (*visited)[3] = malloc((size_t)capacity * sizeof(*visited));
    if (!visited) return 0;

    while (1) {
        m = d * a - m;
        d = (n - m * m) / d;
        a = (a0 + m) / d;

        /* Cycle closes when a triple repeats; the period is the count seen so far. */
        int found = 0;
        for (int i = 0; i < period; i++) {
            if (visited[i][0] == m && visited[i][1] == d && visited[i][2] == a) {
                found = 1;
                break;
            }
        }
        if (found) break;

        if (period >= capacity) {
            capacity *= 2;
            /* Use a temporary so a failed realloc does not leak the existing buffer. */
            int (*tmp)[3] = realloc(visited, (size_t)capacity * sizeof(*visited));
            if (!tmp) { free(visited); return 0; }
            visited = tmp;
        }
        visited[period][0] = m;
        visited[period][1] = d;
        visited[period][2] = a;
        period++;
    }

    free(visited);
    return period;
}

/* Count non-square N <= limit whose sqrt(N) continued fraction has odd period;
   skips perfect squares and tallies odd periods; O(limit * sqrt(limit)). */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int max_limit = parse_int(argv[1]);
    long long count = 0;

    for (int n = 2; n <= max_limit; n++) {
        int sq = (int)sqrt((double)n);
        /* Correct the double-based sqrt to the exact integer floor before the square test. */
        while ((long long)(sq + 1) * (sq + 1) <= n) sq++;
        while ((long long)sq * sq > n) sq--;
        if ((long long)sq * sq == n) continue; /* skip perfect squares (rational roots) */

        int period = get_period_length(n);
        if (period % 2 == 1) count++;
    }

    { snprintf(_answer, sizeof _answer, "%lld", (long long)(count)); return _answer; }
}