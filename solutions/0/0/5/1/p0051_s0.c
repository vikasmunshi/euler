/* Solution to Euler Problem 51: Prime Digit Replacements. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

/* Sundaram sieve: returns array of primes up to max_num, sets *count */
static int *sundaram_sieve(int max_num, int *count) {
    if (max_num < 2) {
        *count = 0;
        return NULL;
    }
    long long n = ((long long)max_num - 1) / 2;
    unsigned char *marked = calloc((size_t)(n + 1), 1);
    if (!marked) { *count = 0; return NULL; }

    for (long long i = 1; i <= n; i++) {
        long long j = i;
        while (i + j + 2LL * i * j <= n) {
            marked[i + j + 2LL * i * j] = 1;
            j++;
        }
    }

    /* Count primes */
    long long cnt = (max_num >= 2) ? 1 : 0; /* for 2 */
    for (long long i = 1; i <= n; i++) {
        if (!marked[i]) cnt++;
    }

    int *primes = malloc((size_t)cnt * sizeof(int));
    if (!primes) { free(marked); *count = 0; return NULL; }

    int idx = 0;
    if (max_num >= 2) primes[idx++] = 2;
    for (long long i = 1; i <= n; i++) {
        if (!marked[i]) primes[idx++] = (int)(2 * i + 1);
    }

    free(marked);
    *count = (int)cnt;
    return primes;
}

static int is_prime(int num) {
    if (num < 2) return 0;
    if (num == 2) return 1;
    if (num % 2 == 0) return 0;
    for (int i = 3; (long long)i * i <= num; i += 2) {
        if (num % i == 0) return 0;
    }
    return 1;
}

long long solve(int argc, char *argv[]) {
    int num_digits = atoi(argv[1]);
    int prime_run  = atoi(argv[2]);

    /* Compute 10^num_digits */
    int limit = 1;
    for (int i = 0; i < num_digits; i++) limit *= 10;

    int prime_count = 0;
    int *primes = sundaram_sieve(limit, &prime_count);
    if (!primes) return -1;

    long long answer = -1;

    for (int pi = 0; pi < prime_count && answer < 0; pi++) {
        int prime = primes[pi];

        /* Convert prime to string */
        char prime_str[32];
        snprintf(prime_str, sizeof(prime_str), "%d", prime);
        int plen = (int)strlen(prime_str);

        /* Iterate over replaced digits: "0123456789"[:10 - prime_run] */
        int max_replaced_digit = 10 - prime_run; /* exclusive upper bound */
        for (int rd = 0; rd < max_replaced_digit && answer < 0; rd++) {
            char replaced = (char)('0' + rd);

            /* Check if this digit appears in prime_str */
            int found = 0;
            for (int k = 0; k < plen; k++) {
                if (prime_str[k] == replaced) { found = 1; break; }
            }
            if (!found) continue;

            /* For each replacement digit >= replaced digit,
               replace all occurrences of 'replaced' with 'replacement',
               check if result >= prime and is prime, count them */
            int seq_count = 0;

            for (int rep = rd; rep <= 9; rep++) {
                char replacement = (char)('0' + rep);

                /* Build new number string */
                char new_str[32];
                int ni = 0;
                for (int k = 0; k < plen; k++) {
                    if (prime_str[k] == replaced)
                        new_str[ni++] = replacement;
                    else
                        new_str[ni++] = prime_str[k];
                }
                new_str[ni] = '\0';

                /* Skip leading zeros: if first char is '0', skip */
                if (new_str[0] == '0') continue;

                int new_val = atoi(new_str);

                if (new_val >= prime && is_prime(new_val)) {
                    seq_count++;
                }
            }

            if (seq_count == prime_run) {
                answer = (long long)prime;
            }
        }
    }

    free(primes);
    return answer;
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