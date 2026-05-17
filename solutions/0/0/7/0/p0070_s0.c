/* Solution to Euler Problem 70: Totient Permutation. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <time.h>

/* Simple sieve to generate primes up to max_val */
static int *sieve_primes(int max_val, int *count) {
    char *is_composite = calloc((size_t)(max_val + 1), 1);
    if (!is_composite) { *count = 0; return NULL; }
    int cap = (int)(max_val / (log((double)max_val) - 1.1)) + 1000;
    int *primes = malloc((size_t)cap * sizeof(int));
    if (!primes) { free(is_composite); *count = 0; return NULL; }
    int n = 0;
    for (int i = 2; i <= max_val; i++) {
        if (!is_composite[i]) {
            primes[n++] = i;
            if (n >= cap) {
                cap *= 2;
                int *tmp = realloc(primes, (size_t)cap * sizeof(int));
                if (!tmp) { free(primes); free(is_composite); *count = 0; return NULL; }
                primes = tmp;
            }
            if ((long long)i * i <= max_val) {
                for (long long j = (long long)i * i; j <= max_val; j += i)
                    is_composite[j] = 1;
            }
        }
    }
    free(is_composite);
    *count = n;
    return primes;
}

/* Check if digits of a and b are permutations of each other */
static int is_digit_permutation(long long a, long long b) {
    int count[10] = {0};
    while (a > 0) { count[a % 10]++; a /= 10; }
    while (b > 0) { count[b % 10]--; b /= 10; }
    for (int i = 0; i < 10; i++)
        if (count[i] != 0) return 0;
    return 1;
}

long long solve(int argc, char *argv[]) {
    int limit = (argc > 1) ? atoi(argv[1]) : 10000000;
    int sqrt_n = (int)sqrt((double)limit);
    int min_prime_1 = sqrt_n / 2;
    int max_prime_1 = sqrt_n;
    int max_prime_2 = limit; /* upper bound for sieve */

    int pcount = 0;
    int *primes = sieve_primes(max_prime_2, &pcount);
    if (!primes) return -1;

    double min_ratio = 1e18;
    long long min_n = 0;

    /* Find range of prime_1 indices */
    int idx1_start = 0;
    while (idx1_start < pcount && primes[idx1_start] <= min_prime_1)
        idx1_start++;
    /* primes[idx1_start] is first prime > min_prime_1 */

    for (int i = idx1_start; i < pcount; i++) {
        long long p1 = primes[i];
        if (p1 > max_prime_1) break;

        long long max_p2 = limit / p1;
        long long min_p2 = p1 + 2;

        /* Find starting index for prime_2 */
        int idx2_start = i + 1;
        while (idx2_start < pcount && primes[idx2_start] <= min_p2)
            idx2_start++;
        /* primes[idx2_start] is first prime > min_p2 (i.e. > p1+2, so >= p1+3,
           but we want prime > p1+2 meaning prime_2 > prime_1+2)
           Actually we want prime_2 > min_prime_2 = p1+2, so prime_2 >= p1+3 but prime */
        /* Re-check: min_prime_2 = prime_1 + 2, we want p > min_prime_2 */
        /* Reset: find first prime strictly greater than p1+2 */
        idx2_start = i + 1;
        while (idx2_start < pcount && primes[idx2_start] <= (int)(p1 + 2))
            idx2_start++;

        for (int j = idx2_start; j < pcount; j++) {
            long long p2 = primes[j];
            if (p2 > max_p2) break;

            long long number = p1 * p2;
            long long totient = (p1 - 1) * (p2 - 1);

            if (is_digit_permutation(number, totient)) {
                double ratio = (double)number / (double)totient;
                if (ratio < min_ratio) {
                    min_ratio = ratio;
                    min_n = number;
                }
            }
        }
    }

    free(primes);
    return min_n;
}

/* Usage: ./file <kwarg>... [--runs=1] [--show]
 * Output: "<runs> <avg_seconds> <result>" */
int main(int argc, char *argv[]) {
    int runs = 1;

    char **solve_argv = malloc((size_t)argc * sizeof(char *));
    if (!solve_argv) {
        fprintf(stderr, "runner: out of memory\n");
        return 1;
    }
    int solve_argc = 0;
    solve_argv[solve_argc++] = argv[0];

    for (int i = 1; i < argc; i++) {
        if (argv[i][0] == '\0') continue;
        if (strncmp(argv[i], "--runs=", 7) == 0) {
            int r = atoi(argv[i] + 7);
            if (r >= 1) runs = r;
            continue;
        }
        if (strcmp(argv[i], "--show") == 0) continue;
        solve_argv[solve_argc++] = argv[i];
    }

    long long result = 0;
    double total = 0.0;
    int rc = 0;
    int has_result = 0;

    for (int r = 0; r < runs; r++) {
        struct timespec t0, t1;
        clock_gettime(CLOCK_MONOTONIC, &t0);
        long long cur = solve(solve_argc, solve_argv);
        clock_gettime(CLOCK_MONOTONIC, &t1);
        total += (double)(t1.tv_sec - t0.tv_sec)
               + (double)(t1.tv_nsec - t0.tv_nsec) * 1e-9;
        if (has_result && cur != result) {
            fprintf(stderr, "Expected consistent result, got %lld previous result=%lld\n",
                    cur, result);
            rc = 1;
        }
        result = cur;
        has_result = 1;
    }

    free(solve_argv);
    printf("%d %.17g %lld\n", runs, total / (double)runs, result);
    return rc;
}