/* Solution to Euler Problem 39: Integer Right Triangles. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
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
    int max_perimeter = atoi(argv[1]);

    int *counts = calloc((size_t)(max_perimeter + 1), sizeof(int));
    if (!counts) {
        fprintf(stderr, "out of memory\n");
        return -1;
    }

    /* Python n bound: range(1, (int(8*max_perimeter**0.5) - 6) // 8, 1)
     * i.e. n < (int(8*sqrt(max_perimeter)) - 6) / 8
     */
    int n_limit = ((int)(8.0 * sqrt((double)max_perimeter)) - 6) / 8;

    for (int n = 1; n < n_limit; n++) {
        /* Python m bound: range(n+1, (int((4+8*max_perimeter)**0.5) - 2*n) // 4, 2)
         * i.e. m < (int(sqrt(4+8*max_perimeter)) - 2*n) / 4
         */
        int m_limit = ((int)(sqrt(4.0 + 8.0 * (double)max_perimeter)) - 2 * n) / 4;

        for (int m = n + 1; m < m_limit; m += 2) {
            if (gcd(m, n) != 1) continue;
            int p0 = 2 * m * (m + n);
            if (p0 > max_perimeter) break;

            /* Python: append p0, then for k in range(2, max_perimeter // p0): append k*p0 */
            if (p0 <= max_perimeter) {
                counts[p0]++;
            }
            int k_limit = max_perimeter / p0;
            for (int k = 2; k < k_limit; k++) {
                counts[k * p0]++;
            }
        }
    }

    int best_p = 0;
    int best_count = 0;
    for (int p = 1; p <= max_perimeter; p++) {
        if (counts[p] > best_count) {
            best_count = counts[p];
            best_p = p;
        }
    }

    free(counts);
    return (long long)best_p;
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