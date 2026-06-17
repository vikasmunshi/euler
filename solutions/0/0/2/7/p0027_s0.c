/* Solution to Euler Problem 27: Quadratic Primes. */
#include "runner.h"
#include <math.h>

/* Test primality by trial division up to sqrt(num); O(sqrt(num)). */
static int is_prime(long long num) {
    if (num < 2) return 0;
    if (num == 2) return 1;
    if (num % 2 == 0) return 0;
    for (long long i = 3; i * i <= num; i += 2) {
        if (num % i == 0) return 0;
    }
    return 1;
}

/* Length of the unbroken prime run of |n^2 + a*n + b| for n = 0, 1, 2, ... */
static int prime_run(int a, int b) {
    int x = 0;
    while (1) {
        /* hold value in long long: the quadratic can reach ~2 * 10^6 */
        long long val = (long long)x * x + (long long)a * x + b;
        if (val < 0) val = -val;
        if (!is_prime(val)) break;
        x++;
    }
    return x;
}

/* Sieve of Sundaram: return primes up to max_num (odd-only marking); sets count. */
static int *primes_sundaram_sieve(int max_num, int *count) {
    *count = 0;
    if (max_num < 2) return NULL;

    int n = (max_num - 1) / 2;
    unsigned char *marked = calloc((size_t)(n + 1), 1);
    if (!marked) return NULL;

    for (int i = 1; i <= n; i++) {
        int j = i;
        while (i + j + 2 * i * j <= n) {
            marked[i + j + 2 * i * j] = 1;
            j++;
        }
    }

    /* Count primes */
    int cap = 1; /* for 2 */
    for (int i = 1; i <= n; i++) {
        if (!marked[i]) cap++;
    }

    int *primes = malloc((size_t)cap * sizeof(int));
    if (!primes) { free(marked); return NULL; }

    int idx = 0;
    primes[idx++] = 2;
    for (int i = 1; i <= n; i++) {
        if (!marked[i]) primes[idx++] = 2 * i + 1;
    }

    free(marked);
    *count = idx;
    return primes;
}

/* Brute-force scan pruned by the n=0 constraint (b must be prime) and a-parity.
   Since n=0 yields b, only prime b can start a run; iterate non-negative
   magnitudes of a and apply the four sign variants. O(P * A * R * sqrt(V_max)). */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int max_limit = parse_int(argv[1]);

    int prime_count = 0;
    int *primes = primes_sundaram_sieve(max_limit, &prime_count);
    if (!primes) { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }

    int best_run = 0;
    long long best_product = 0;

    for (int pi = 0; pi < prime_count; pi++) {
        int b = primes[pi];

        /* a starts at 0 if b==2, else 1; step by 2 (odd a for odd b) */
        int a_start = (b == 2) ? 0 : 1;
        int a_step  = (b == 2) ? 1 : 2;

        for (int a = a_start; a < max_limit; a += a_step) {
            /* Try all four sign combinations: (a,b), (a,-b), (-a,-b), (-a,b) */
            int combos_a[4] = { a,  a, -a, -a};
            int combos_b[4] = { b, -b, -b,  b};
            long long products[4] = { (long long)a*b, -(long long)a*b,
                                       (long long)a*b, -(long long)a*b };

            for (int c = 0; c < 4; c++) {
                int run = prime_run(combos_a[c], combos_b[c]);
                if (run > best_run) {
                    best_run = run;
                    best_product = products[c];
                } else if (run == best_run) {
                    /* tie-break: replicate Python max() on (run, product), keeping the larger product */
                    if (products[c] > best_product) {
                        best_product = products[c];
                    }
                }
            }
        }
    }

    free(primes);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(best_product)); return _answer; }
}