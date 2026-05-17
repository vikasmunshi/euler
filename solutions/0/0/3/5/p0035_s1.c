/* Solution to Euler Problem 35: Circular Primes. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static void primes_sieve(int max_num, char *sieve) {
    /* sieve[i] = 1 means prime */
    if (max_num < 2) return;
    for (int i = 2; i <= max_num; i++) sieve[i] = 1;
    for (int i = 2; (long long)i * i <= max_num; i++) {
        if (sieve[i]) {
            for (int j = i * i; j <= max_num; j += i) {
                sieve[j] = 0;
            }
        }
    }
}

static int get_rotated_numbers(int num, int *rotations) {
    char str_num[12];
    snprintf(str_num, sizeof(str_num), "%d", num);
    int len = (int)strlen(str_num);
    int count = 0;
    if (len == 1) {
        rotations[count++] = num;
        return count;
    }
    char buf[12];
    for (int i = 1; i <= len; i++) {
        int pos = 0;
        for (int j = i; j < len; j++) buf[pos++] = str_num[j];
        for (int j = 0; j < i; j++) buf[pos++] = str_num[j];
        buf[pos] = '\0';
        rotations[count++] = atoi(buf);
    }
    return count;
}

static int has_bad_digit(int num) {
    char str_num[12];
    snprintf(str_num, sizeof(str_num), "%d", num);
    for (int i = 0; str_num[i]; i++) {
        char c = str_num[i];
        if (c == '0' || c == '2' || c == '4' || c == '5' || c == '6' || c == '8')
            return 1;
    }
    return 0;
}

long long solve(int argc, char *argv[]) {
    int max_limit = atoi(argv[1]);

    /* Generate primes up to max(max_limit, 1000000) as in the Python s1 solution */
    int gen_limit = max_limit > 1000000 ? max_limit : 1000000;

    char *sieve_full = calloc((size_t)(gen_limit + 1), 1);
    if (!sieve_full) {
        fprintf(stderr, "out of memory\n");
        return -1;
    }
    primes_sieve(gen_limit, sieve_full);

    /* Build a lookup sieve limited to max_limit for rotation checks */
    /* (rotations of numbers <= max_limit are also <= max_limit in digit count,
       but could numerically exceed max_limit; treat those as non-prime for our purposes) */

    int count = 0;
    int rotations[12];

    for (int prime = 2; prime <= max_limit; prime++) {
        if (!sieve_full[prime]) continue;

        if (prime < 10) {
            count++;
            continue;
        }

        if (has_bad_digit(prime)) continue;

        int num_rot = get_rotated_numbers(prime, rotations);
        int all_prime = 1;
        for (int r = 0; r < num_rot; r++) {
            int rot = rotations[r];
            if (rot > max_limit || !sieve_full[rot]) {
                all_prime = 0;
                break;
            }
        }
        if (all_prime) count++;
    }

    free(sieve_full);
    return count;
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