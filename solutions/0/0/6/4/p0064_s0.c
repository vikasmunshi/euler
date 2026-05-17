/* Solution to Euler Problem 64: Odd Period Square Roots. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <time.h>

static int get_period_length(int n) {
    int a0 = (int)sqrt((double)n);
    /* Confirm isqrt */
    while ((long long)(a0 + 1) * (a0 + 1) <= n) a0++;
    while ((long long)a0 * a0 > n) a0--;

    int a = a0;
    int d = 1, m = 0;
    int period = 0;

    /* Store visited (m, d, a) triples */
    int capacity = 64;
    int (*visited)[3] = malloc((size_t)capacity * sizeof(*visited));
    if (!visited) return 0;

    while (1) {
        m = d * a - m;
        d = (n - m * m) / d;
        a = (a0 + m) / d;

        /* Check if (m, d, a) already visited */
        int found = 0;
        for (int i = 0; i < period; i++) {
            if (visited[i][0] == m && visited[i][1] == d && visited[i][2] == a) {
                found = 1;
                break;
            }
        }
        if (found) break;

        /* Add to visited */
        if (period >= capacity) {
            capacity *= 2;
            int (*tmp)[3] = realloc(visited, (size_t)capacity * sizeof(*visited));
            if (!tmp) { free(visited); return 0; }
            visited = tmp;
        }
        visited[period][0] = m;
        visited[period][1] = d;
        visited[period][2] = a;
        period++;
    }

    free(visited);
    return period;
}

long long solve(int argc, char *argv[]) {
    int max_limit = atoi(argv[1]);
    long long count = 0;

    for (int n = 2; n <= max_limit; n++) {
        int sq = (int)sqrt((double)n);
        /* Adjust for perfect squares */
        while ((long long)(sq + 1) * (sq + 1) <= n) sq++;
        while ((long long)sq * sq > n) sq--;
        if ((long long)sq * sq == n) continue; /* skip perfect squares */

        int period = get_period_length(n);
        if (period % 2 == 1) count++;
    }

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