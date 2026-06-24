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

/* Scan triangular numbers T(i)=i(i+1)/2; since gcd(i, i+1)=1, d(T(i)) is the product of the
   divisor counts of the two coprime halves (one carrying the /2). O(sqrt(T(i))) per step. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int num_divisors = parse_int(argv[1]);
    long long i = 1;
    long long triangle_number = 1;
    while (1) {
        int factors_i, factors_next;
        if (i % 2 == 0) {
            factors_i    = num_factors(i / 2);
            factors_next = num_factors(i + 1);
        } else {
            factors_i    = num_factors(i);
            factors_next = num_factors((i + 1) / 2);
        }
        int divisor_count = factors_i * factors_next;
        if (divisor_count > num_divisors) {
            { snprintf(_answer, sizeof _answer, "%lld", (long long)(triangle_number)); return _answer; }
        }
        i++;
        triangle_number = i * (i + 1) / 2;
    }
}
