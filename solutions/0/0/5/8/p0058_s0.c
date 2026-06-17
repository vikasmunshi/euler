/* Solution to Euler Problem 58: Spiral Primes. */
#include "runner.h"

/* Trial division by odd divisors up to sqrt(num); O(sqrt(num)). */
static int is_prime(long long num) {
    if (num < 2) return 0;
    if (num == 2) return 1;
    if (num % 2 == 0) return 0;
    for (long long i = 3; i * i <= num; i += 2) {
        if (num % i == 0) return 0;
    }
    return 1;
}

/* Scan spiral layers, counting prime diagonal corners (arithmetic from (2k+1)^2) until the
   running ratio drops below the threshold; O(n^2) in side length n, dominated by trial division. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    double threshold = (argc > 1) ? atof(argv[1]) : 0.1;

    long long num_prime_diagonals = 0;
    long long num_diagonal_elements = 1;

    for (int layer = 1; ; layer++) {
        int side_length = 2 * layer + 1;
        long long side_length_min_1 = side_length - 1;
        /* Corners exceed 32-bit range near the answer, so compute them as long long. */
        long long bottom_right = (long long)side_length * side_length;
        long long bottom_left = bottom_right - side_length_min_1;
        long long top_left = bottom_left - side_length_min_1;
        long long top_right = top_left - side_length_min_1;

        num_diagonal_elements += 4;
        num_prime_diagonals += is_prime(bottom_right);
        num_prime_diagonals += is_prime(bottom_left);
        num_prime_diagonals += is_prime(top_left);
        num_prime_diagonals += is_prime(top_right);

        if ((double)num_prime_diagonals / (double)num_diagonal_elements < threshold) {
            { snprintf(_answer, sizeof _answer, "%lld", (long long)(side_length)); return _answer; }
        }
    }
}