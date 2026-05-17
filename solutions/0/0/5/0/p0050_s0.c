/* Solution to Euler Problem 50: Consecutive Prime Sum. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static int *primes_sundaram_sieve(int max_num, int *out_count) {
    *out_count = 0;
    if (max_num < 2) {
        int *p = malloc(sizeof(int));
        return p; /* return empty but non-null */
    }

    int n = (max_num - 1) / 2;
    unsigned char *marked = calloc((size_t)(n + 1), 1);
    if (!marked) return NULL;

    for (int i = 1; i <= n; i++) {
        for (int j = i; (long long)i + j + 2LL * i * j <= n; j++) {
            marked[i + j + 2 * i * j] = 1;
        }
    }

    int count = 1; /* for prime 2 */
    for (int i = 1; i <= n; i++) {
        if (!marked[i]) count++;
    }

    int *primes = malloc((size_t)count * sizeof(int));
    if (!primes) { free(marked); return NULL; }

    int idx = 0;
    primes[idx++] = 2;
    for (int i = 1; i <= n; i++) {
        if (!marked[i]) primes[idx++] = 2 * i + 1;
    }

    free(marked);
    *out_count = count;
    return primes;
}

long long solve(int argc, char *argv[]) {
    int max_limit = (argc > 1) ? atoi(argv[1]) : 1000000;
    if (max_limit < 2) return 0;

    int prime_count = 0;
    int *primes = primes_sundaram_sieve(max_limit, &prime_count);
    if (!primes || prime_count == 0) {
        free(primes);
        return 0;
    }

    /* prefix sums array of size prime_count+1 */
    long long *prime_sums = malloc((size_t)(prime_count + 1) * sizeof(long long));
    if (!prime_sums) { free(primes); return -1; }

    prime_sums[0] = 0;
    for (int i = 0; i < prime_count; i++) {
        prime_sums[i + 1] = prime_sums[i] + primes[i];
    }

    /* boolean sieve for primality checks, size max_limit+1 */
    unsigned char *is_prime = calloc((size_t)(max_limit + 1), 1);
    if (!is_prime) { free(prime_sums); free(primes); return -1; }
    for (int i = 0; i < prime_count; i++) {
        if (primes[i] <= max_limit)
            is_prime[primes[i]] = 1;
    }

    int best_length = 0;
    long long best_prime = 0;

    /* len of prime_sums is prime_count+1, indices 0..prime_count */
    int ps_len = prime_count + 1;

    for (int i = 0; i < ps_len; i++) {
        int j_start = i - best_length - 1;
        if (j_start < 0) continue; /* can't beat current best */
        for (int j = j_start; j >= 0; j--) {
            long long possible_prime = prime_sums[i] - prime_sums[j];
            if (possible_prime > (long long)max_limit) break;
            if (possible_prime >= 2) {
                int pp = (int)possible_prime;
                if (is_prime[pp]) {
                    best_length = i - j;
                    best_prime = possible_prime;
                }
            }
        }
    }

    free(is_prime);
    free(prime_sums);
    free(primes);

    return best_prime;
}

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