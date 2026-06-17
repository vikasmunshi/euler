/* Solution to Euler Problem 75: Singular Integer Right Triangles. */
#include "runner.h"
#include <math.h>

/* Euclidean gcd; used to keep only primitive (m, n) generators. */
static int gcd(int a, int b) {
    while (b) {
        int t = b;
        b = a % b;
        a = t;
    }
    return a;
}

/*
 * Euclid's formula sieve: every primitive Pythagorean triple comes from a unique (m, n) with
 * m > n > 0, gcd(m, n) = 1, opposite parity, and has perimeter p = 2m(m + n). Enumerate those
 * generators (m bounded by sqrt(max_perimeter / 2)), then sieve-mark every multiple k*p <= limit
 * in a flat count array; the answer is the number of perimeters hit exactly once. O(L log L).
 */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int max_perimeter = parse_int(argv[1]);

    /* Dense domain: index directly by perimeter value; calloc zero-inits in one step. */
    int *perimeter_count = calloc((size_t)(max_perimeter + 1), sizeof(int));
    if (!perimeter_count) {
        fprintf(stderr, "Out of memory\n");
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }

    int m_max = (int)sqrt((double)max_perimeter / 2.0);

    for (int m = 2; m <= m_max; m++) {
        /* n starts at m%2+1 and steps by 2 so m-n is always odd: opposite parity for free. */
        int n_start = m % 2 + 1;
        for (int n = n_start; n < m; n += 2) {
            if (gcd(m, n) != 1)
                continue;
            int p = 2 * m * (m + n);
            int k = 1;
            /* Widen k*p to long long to avoid 32-bit overflow at large limits. */
            while ((long long)k * p <= max_perimeter) {
                perimeter_count[k * p]++;
                k++;
            }
        }
    }

    long long count = 0;
    for (int i = 1; i <= max_perimeter; i++) {
        if (perimeter_count[i] == 1)
            count++;
    }

    free(perimeter_count);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(count)); return _answer; }
}