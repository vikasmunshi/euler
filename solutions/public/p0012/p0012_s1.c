/* Solution to Euler Problem 12: Highly Divisible Triangular Number. */
#include "runner.h"

/* Count divisors of n via trial division to sqrt(n): product of (exponent + 1). */
static int num_factors(long long n) {
    if (n <= 0) return 0;
    int result = 1;
    long long d = 2;
    while (d * d <= n) {
        if (n % d == 0) {
            int exp = 0;
            while (n % d == 0) {
                n /= d;
                exp++;
            }
            result *= exp + 1;
        }
        d++;
    }
    if (n > 1) result *= 2;  /* leftover residue is a prime with exponent 1 */
    return result;
}

/* Direct search: factor each whole triangular number T(i)=i(i+1)/2 and count its divisors
   until the count exceeds the target. O(sqrt(T(i))) per step. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int num_divisors = parse_int(argv[1]);
    long long i = 1;
    long long triangle_number = 1;
    while (num_factors(triangle_number) < num_divisors) {
        i++;
        triangle_number = i * (i + 1) / 2;
    }
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(triangle_number)); return _answer; }
}
