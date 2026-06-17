/* Solution to Euler Problem 39: Integer Right Triangles. */
#include "runner.h"
#include <math.h>

/* Iterative Euclidean algorithm returning gcd(a, b). */
static int gcd(int a, int b) {
    while (b) {
        int t = b;
        b = a % b;
        a = t;
    }
    return a;
}

/* Enumerate primitive Pythagorean triples via Euclid's formula
 * (a = m^2 - n^2, b = 2mn, c = m^2 + n^2 with m > n > 0, gcd(m, n) = 1,
 * opposite parity), whose primitive perimeter is p0 = 2m(m + n), then tally
 * every multiple k*p0 <= max_perimeter in a value-indexed counting array and
 * scan it for the perimeter with the most triples. Opposite parity is enforced
 * structurally (m starts at n+1, steps by 2); the loop bounds invert the
 * perimeter formula to closed form. O(P log P) over the perimeter limit P. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int max_perimeter = parse_int(argv[1]);

    /* counts[p] holds the number of integer right triangles of perimeter p;
     * calloc zero-initialises the dense value-indexed frequency table. */
    int *counts = calloc((size_t)(max_perimeter + 1), sizeof(int));
    if (!counts) {
        fprintf(stderr, "out of memory\n");
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }

    /* Smallest valid m for a given n is n+1; substituting into
     * p0 = 2m(m + n) <= P and solving for n gives this closed-form bound. */
    int n_limit = ((int)(8.0 * sqrt((double)max_perimeter)) - 6) / 8;

    for (int n = 1; n < n_limit; n++) {
        /* Solving 2m^2 + 2mn <= P for m via the quadratic formula gives this
         * upper limit, so almost every iteration yields an in-range perimeter. */
        int m_limit = ((int)(sqrt(4.0 + 8.0 * (double)max_perimeter)) - 2 * n) / 4;

        for (int m = n + 1; m < m_limit; m += 2) {
            if (gcd(m, n) != 1) continue;
            int p0 = 2 * m * (m + n);
            /* Guard against a slightly loose floating-point loop bound. */
            if (p0 > max_perimeter) break;

            /* Count the primitive perimeter, then every scaled multiple. */
            if (p0 <= max_perimeter) {
                counts[p0]++;
            }
            int k_limit = max_perimeter / p0;
            for (int k = 2; k < k_limit; k++) {
                counts[k * p0]++;
            }
        }
    }

    /* Linear scan for the perimeter with the maximum triangle count. */
    int best_p = 0;
    int best_count = 0;
    for (int p = 1; p <= max_perimeter; p++) {
        if (counts[p] > best_count) {
            best_count = counts[p];
            best_p = p;
        }
    }

    free(counts);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)((long long)best_p)); return _answer; }
}