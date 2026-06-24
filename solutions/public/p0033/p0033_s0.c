/* Solution to Euler Problem 33: Digit Cancelling Fractions. */
#include "runner.h"

/* Iterative Euclidean GCD: repeatedly (a, b) -> (b, a % b) until b is zero; O(log(min(a, b))). */
static long long gcd(long long a, long long b) {
    while (b) {
        long long t = b;
        b = a % b;
        a = t;
    }
    return a;
}

/*
 * Brute-force enumeration of two-digit numerator/denominator pairs sharing a digit, testing the
 * naive-cancellation condition via the cross-multiplied integer identity
 * (10*numerator + x) * denominator == (10*x + denominator) * numerator, which avoids floating point.
 * Accumulates the matching numerators and denominators separately, then reduces the pair with
 * gcd to report the lowest-terms denominator; constant-size scan, O(1).
 */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    (void)argc; (void)argv;

    long long num_product = 1;
    long long den_product = 1;

    for (int denominator = 2; denominator <= 9; denominator++) {
        for (int numerator = 1; numerator < denominator; numerator++) {
            for (int x = 1; x <= 9; x++) {
                if (x == denominator || x == numerator) continue;
                if ((10 * numerator + x) * denominator == (10 * x + denominator) * numerator) {
                    num_product *= numerator;
                    den_product *= denominator;
                }
            }
        }
    }

    long long g = gcd(num_product, den_product);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(den_product / g)); return _answer; }
}