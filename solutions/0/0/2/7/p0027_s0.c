/* Solution to Euler Problem 27: Quadratic Primes. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <time.h>

static int is_prime(long long num) {
    if (num < 2) return 0;
    if (num == 2) return 1;
    if (num % 2 == 0) return 0;
    for (long long i = 3; i * i <= num; i += 2) {
        if (num % i == 0) return 0;
    }
    return 1;
}

static int prime_run(int a, int b) {
    int x = 0;
    while (1) {
        long long val = (long long)x * x + (long long)a * x + b;
        if (val < 0) val = -val;
        if (!is_prime(val)) break;
        x++;
    }
    return x;
}

/* Sundaram sieve: returns array of primes up to max_num, sets count */
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

long long solve(int argc, char *argv[]) {
    int max_limit = atoi(argv[1]);

    int prime_count = 0;
    int *primes = primes_sundaram_sieve(max_limit, &prime_count);
    if (!primes) return -1;

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
                    /* tie-break: Python uses max() on tuples, so same run keeps first found */
                    /* Actually Python max picks the largest product on tie; replicate that */
                    if (products[c] > best_product) {
                        best_product = products[c];
                    }
                }
            }
        }
    }

    free(primes);
    return best_product;
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