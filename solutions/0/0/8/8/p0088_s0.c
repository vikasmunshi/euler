/* Solution to Euler Problem 88: Product-sum Numbers. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static int g_max_k;
static int *g_min_prod;

static void find_product_sum(int prod, int total, int count, int start) {
    int k = prod - total + count;
    if (k < g_max_k) {
        if (prod < g_min_prod[k]) {
            g_min_prod[k] = prod;
        }
        int limit = g_max_k / prod * 2 + 1;
        for (int i = start; i <= limit; i++) {
            find_product_sum(prod * i, total + i, count + 1, i);
        }
    }
}

long long solve(int argc, char *argv[]) {
    int max_k = atoi(argv[1]);
    int min_k = atoi(argv[2]);
    max_k += 1;

    g_max_k = max_k;
    g_min_prod = malloc((size_t)max_k * sizeof(int));
    if (!g_min_prod) {
        fprintf(stderr, "out of memory\n");
        return -1;
    }
    for (int i = 0; i < max_k; i++) {
        g_min_prod[i] = 2 * max_k;
    }

    find_product_sum(1, 1, 1, min_k);

    /* Sum unique values from min_prod[2:] */
    /* Use a boolean array indexed by value to deduplicate */
    int upper = 2 * max_k + 1;
    char *seen = calloc((size_t)upper, sizeof(char));
    if (!seen) {
        fprintf(stderr, "out of memory\n");
        free(g_min_prod);
        return -1;
    }

    long long result = 0;
    for (int k = 2; k < max_k; k++) {
        int v = g_min_prod[k];
        if (v < upper && !seen[v]) {
            seen[v] = 1;
            result += v;
        }
    }

    free(seen);
    free(g_min_prod);
    g_min_prod = NULL;
    return result;
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