/* Solution to Euler Problem 47: Distinct Primes Factors. */
#include "runner.h"

/* Count distinct prime factors of n by trial division with in-place reduction; O(sqrt(n)). */
static int prime_factor_count(int n) {
    if (n <= 1) return 0;
    int count = 0;
    int d = 2;
    while (d * d <= n) {
        if (n % d == 0) {
            count++;
            /* Strip every copy of d so later composite d cannot divide; each divisor found is prime. */
            while (n % d == 0) {
                n /= d;
            }
        }
        d++;
    }
    /* Any remainder above 1 is a prime factor exceeding the square root of the original n. */
    if (n > 1) count++;
    return count;
}

/* Linear scan for the first run of n consecutive integers each with n distinct prime factors.
   Each count is O(sqrt(k)) trial division; the window test short-circuits on the first failure,
   giving roughly O(answer * sqrt(answer)) overall. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int n = parse_int(argv[1]);
    int number = 2;
    while (1) {
        int all_match = 1;
        for (int i = 0; i < n; i++) {
            if (prime_factor_count(number + i) != n) {
                all_match = 0;
                break;
            }
        }
        if (all_match) { snprintf(_answer, sizeof _answer, "%lld", (long long)((long long)number)); return _answer; }
        number++;
    }
}