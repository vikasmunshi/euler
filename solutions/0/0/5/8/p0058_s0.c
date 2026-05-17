/* Solution to Euler Problem 58: Spiral Primes. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
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

long long solve(int argc, char *argv[]) {
    double threshold = (argc > 1) ? atof(argv[1]) : 0.1;

    long long num_prime_diagonals = 0;
    long long num_diagonal_elements = 1;

    for (int layer = 1; ; layer++) {
        int side_length = 2 * layer + 1;
        long long side_length_min_1 = side_length - 1;
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
            return side_length;
        }
    }
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