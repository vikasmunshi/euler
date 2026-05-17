/* Solution to Euler Problem 38: Pandigital Multiples. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static int is_nine_pandigital(long long n) {
    if (n < 100000000LL || n > 999999999LL)
        return 0;
    int digits[10] = {0};
    while (n) {
        int d = (int)(n % 10);
        if (d == 0 || digits[d] == 1)
            return 0;
        digits[d] = 1;
        n /= 10;
    }
    int sum = 0;
    for (int i = 1; i <= 9; i++) sum += digits[i];
    return sum == 9;
}

long long solve(int argc, char *argv[]) {
    (void)argc; (void)argv;

    /* (n, max_x) pairs as in the Python solution */
    int pairs[8][2] = {
        {2, 9876}, {3, 987}, {4, 98}, {5, 9},
        {6, 9}, {7, 9}, {8, 9}, {9, 9}
    };

    for (int p = 0; p < 8; p++) {
        int n = pairs[p][0];
        int x = pairs[p][1];
        while (x > 0) {
            /* Build concatenated number */
            char buf[64];
            buf[0] = '\0';
            for (int i = 1; i <= n; i++) {
                char tmp[32];
                snprintf(tmp, sizeof(tmp), "%d", i * x);
                strcat(buf, tmp);
            }
            long long number = atoll(buf);
            if (is_nine_pandigital(number)) {
                return number;
            }
            x--;
        }
    }
    return -1; /* No solution found */
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