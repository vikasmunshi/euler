/* Solution to Euler Problem 75: Singular Integer Right Triangles. */
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

    /* Allocate perimeter count array */
    int *perimeter_count = calloc((size_t)(max_perimeter + 1), sizeof(int));
    if (!perimeter_count) {
        fprintf(stderr, "Out of memory\n");
        return -1;
    }

    int m_max = (int)sqrt((double)max_perimeter / 2.0);

    for (int m = 2; m <= m_max; m++) {
        /* n starts at m%2+1 to ensure m-n is odd, steps by 2 */
        int n_start = m % 2 + 1;
        for (int n = n_start; n < m; n += 2) {
            if (gcd(m, n) != 1)
                continue;
            int p = 2 * m * (m + n);
            int k = 1;
            while ((long long)k * p <= max_perimeter) {
                perimeter_count[k * p]++;
                k++;
            }
        }
    }

    long long count = 0;
    for (int i = 1; i <= max_perimeter; i++) {
        if (perimeter_count[i] == 1)
            count++;
    }

    free(perimeter_count);
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