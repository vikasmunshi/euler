/* Solution to Euler Problem 10: Summation of Primes. */
#include "runner.h"
#include <math.h>

/* Test primality by trial division of odd divisors up to sqrt(num). */
static int is_prime(int num) {
    if (num < 2) return 0;
    if (num == 2) return 1;
    if (num % 2 == 0) return 0;
    int i = 3;
    while ((long long)i * i <= num) {
        if (num % i == 0) return 0;
        i += 2;
    }
    return 1;
}

/* Sum primes below max_num by trial-division primality test on each candidate; O(n*sqrt(n)/log n). */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int max_num = parse_int(argv[1]);
    long long sum = 0;
    for (int n = 2; n < max_num; n++) {
        if (is_prime(n)) sum += n;
    }
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(sum)); return _answer; }
}
