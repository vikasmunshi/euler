/* Solution to Euler Problem 73: Counting Fractions in a Range. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static long long rank_fn(int max_d, int n, int d) {
    int len_data = max_d + 1;
    long long *data = malloc((size_t)len_data * sizeof(long long));
    if (!data) return -1;

    for (int i = 0; i < len_data; i++) {
        data[i] = (long long)i * n / d;
    }

    for (int i = 1; i < len_data; i++) {
        for (int j = 2 * i; j < len_data; j += i) {
            data[j] -= data[i];
        }
    }

    long long total = 0;
    for (int i = 0; i < len_data; i++) {
        total += data[i];
    }

    free(data);
    return total;
}

long long solve(int argc, char *argv[]) {
    int max_d = atoi(argv[1]);
    return rank_fn(max_d, 1, 2) - rank_fn(max_d, 1, 3) - 1;
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