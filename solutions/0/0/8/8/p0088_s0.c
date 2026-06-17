/* Solution to Euler Problem 88: Product-sum Numbers. */
#include "runner.h"

static int g_max_k;
static int *g_min_prod;

/* Relax g_min_prod for the set size implied by this factorization, then extend it. */
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

/* Recursive factorization search: each factorization (product P, sum S) of m factors >= 2
   yields a product-sum set of size k = m + (P - S) after padding with P - S ones. The bound
   N <= 2k seeds the table and prunes branches; runtime is near-linear in max_k. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int max_k = parse_int(argv[1]);
    int min_k = parse_int(argv[2]);
    max_k += 1;

    g_max_k = max_k;
    g_min_prod = malloc((size_t)max_k * sizeof(int));
    if (!g_min_prod) {
        fprintf(stderr, "out of memory\n");
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }
    for (int i = 0; i < max_k; i++) {
        g_min_prod[i] = 2 * max_k;
    }

    find_product_sum(1, 1, 1, min_k);

    /* Sum unique minimal values; every value lies in [4, 2*max_k], so deduplicate with a
       direct-address boolean array indexed by value (O(max_value), no sorting or hashing). */
    int upper = 2 * max_k + 1;
    char *seen = calloc((size_t)upper, sizeof(char));
    if (!seen) {
        fprintf(stderr, "out of memory\n");
        free(g_min_prod);
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
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
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(result)); return _answer; }
}