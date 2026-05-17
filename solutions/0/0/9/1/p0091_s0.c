/* Solution to Euler Problem 91: Right Triangles with Integer Coordinates. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static int gcd(int a, int b) {
    while (b) {
        int t = b;
        b = a % b;
        a = t;
    }
    return a;
}

long long solve(int argc, char *argv[]) {
    int coordinate_limit = atoi(argv[1]);

    long long triangles_at_p_or_q = 0;
    for (int x = 1; x <= coordinate_limit; x++) {
        for (int y = 1; y < coordinate_limit; y++) {
            int m = gcd(x, y);
            long long a = (long long)x * m / y;
            long long b = (long long)m * (coordinate_limit - y) / x;
            long long mn = a < b ? a : b;
            triangles_at_p_or_q += mn;
        }
    }
    triangles_at_p_or_q *= 2;

    long long triangles_at_origin = 3LL * coordinate_limit * coordinate_limit;
    return triangles_at_p_or_q + triangles_at_origin;
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