/* Solution to Euler Problem 91: Right Triangles with Integer Coordinates. */
#include "runner.h"

/* Euclidean gcd, used to reduce a vector to its primitive lattice direction; O(log min(a, b)). */
static int gcd(int a, int b) {
    while (b) {
        int t = b;
        b = a % b;
        a = t;
    }
    return a;
}

/*
 * Classify each right triangle by where its right angle sits. The origin contributes exactly
 * 3 * N^2 axis-aligned cases. For a right angle at non-origin P = (x, y) the perpendicular to OP
 * has primitive step (-y/m, x/m) with m = gcd(x, y); the count of lattice points reachable inside
 * the grid is bounded by both the horizontal room (x*m/y) and the vertical room (m*(N-y)/x), and
 * the minimum is the step count. Doubling covers the right angle at Q and the opposite direction.
 * Both divisions are exact because m divides x and y. Overall O(N^2 log N).
 */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int coordinate_limit = parse_int(argv[1]);

    long long triangles_at_p_or_q = 0;
    for (int x = 1; x <= coordinate_limit; x++) {
        for (int y = 1; y < coordinate_limit; y++) {
            int m = gcd(x, y);
            /* Cast to long long before multiplying so x*m cannot overflow 32 bits for large N. */
            long long a = (long long)x * m / y;
            long long b = (long long)m * (coordinate_limit - y) / x;
            long long mn = a < b ? a : b;
            triangles_at_p_or_q += mn;
        }
    }
    triangles_at_p_or_q *= 2;

    long long triangles_at_origin = 3LL * coordinate_limit * coordinate_limit;
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(triangles_at_p_or_q + triangles_at_origin)); return _answer; }
}