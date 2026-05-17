/* Solution to Euler Problem 32: Pandigital Products. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

/* Simple set for storing unique products (at most a few hundred values) */
static int products[10000];
static int product_count = 0;

static void set_add(int val) {
    for (int i = 0; i < product_count; i++) {
        if (products[i] == val) return;
    }
    products[product_count++] = val;
}

static int is_nine_pandigital(int a, int b, int c) {
    /* Concatenate digits of a, b, c and check 1-9 pandigital */
    char buf[20];
    int len = snprintf(buf, sizeof(buf), "%d%d%d", a, b, c);
    if (len != 9) return 0;
    int seen[10] = {0};
    for (int i = 0; i < 9; i++) {
        int d = buf[i] - '0';
        if (d < 1 || d > 9) return 0;
        if (seen[d]) return 0;
        seen[d] = 1;
    }
    return 1;
}

long long solve(int argc, char *argv[]) {
    (void)argc; (void)argv;

    product_count = 0;

    /* nine_digits: 1..9 as characters */
    int digits[9] = {1, 2, 3, 4, 5, 6, 7, 8, 9};

    /* Split configurations: (a_len, b_len) = (1,4) and (2,3) */
    int splits[2][2] = {{1, 4}, {2, 3}};

    for (int s = 0; s < 2; s++) {
        int a_len = splits[s][0];
        int b_len = splits[s][1];

        /* Permutations of digits for 'a' of length a_len */
        /* We iterate over all permutations of 9 digits taken a_len at a time */
        /* Use index arrays */
        int a_perm[4], b_perm[4];
        int a_used[9]; /* indices into digits[] used for a */

        /* Enumerate a_len-permutations from digits */
        /* We'll use a simple recursive-style loop unrolling for small sizes */
        /* Since a_len <= 2 and b_len <= 4, we can use nested loops */

        /* For a: pick a_len distinct indices from 0..8 in order */
        /* For b: pick b_len distinct indices from remaining */

        int ia[4] = {-1, -1, -1, -1};
        int ib[4] = {-1, -1, -1, -1};

        /* Enumerate all ordered selections of a_len from 9 for 'a' */
        /* Then enumerate all ordered selections of b_len from remaining for 'b' */

        /* We'll do this iteratively with a flat approach */
        /* For a_len=1: 9 choices; for a_len=2: 9*8=72 choices */
        /* For b_len=4: remaining 8 choose 4 * 4! = 1680; for b_len=3: 7*6*5=210 */

        /* Use a simple permutation generation with arrays */
        /* Iterate over all permutations using index arrays */

        int ai[2] = {0, 0}; /* indices in digits[] for a */
        int bi[4] = {0, 0, 0, 0}; /* indices in digits[] for b */

        /* Generate all a_len-permutations */
        for (int p0 = 0; p0 < 9; p0++) {
            ai[0] = p0;
            if (a_len == 1) {
                /* a determined */
                int a_val = digits[ai[0]];
                /* Generate all b_len-permutations from remaining digits */
                /* remaining: all except ai[0] */
                int rem[9];
                int rem_count = 0;
                for (int k = 0; k < 9; k++) {
                    if (k != ai[0]) rem[rem_count++] = k;
                }
                /* b_len = 4: permutations of rem taken 4 */
                for (int q0 = 0; q0 < rem_count; q0++) {
                    for (int q1 = 0; q1 < rem_count; q1++) {
                        if (q1 == q0) continue;
                        for (int q2 = 0; q2 < rem_count; q2++) {
                            if (q2 == q0 || q2 == q1) continue;
                            for (int q3 = 0; q3 < rem_count; q3++) {
                                if (q3 == q0 || q3 == q1 || q3 == q2) continue;
                                int b_val = digits[rem[q0]] * 1000
                                          + digits[rem[q1]] * 100
                                          + digits[rem[q2]] * 10
                                          + digits[rem[q3]];
                                int c_val = a_val * b_val;
                                if (is_nine_pandigital(a_val, b_val, c_val)) {
                                    set_add(c_val);
                                }
                            }
                        }
                    }
                }
            } else {
                /* a_len == 2 */
                for (int p1 = 0; p1 < 9; p1++) {
                    if (p1 == p0) continue;
                    ai[1] = p1;
                    int a_val = digits[ai[0]] * 10 + digits[ai[1]];
                    /* remaining: all except ai[0], ai[1] */
                    int rem[9];
                    int rem_count = 0;
                    for (int k = 0; k < 9; k++) {
                        if (k != ai[0] && k != ai[1]) rem[rem_count++] = k;
                    }
                    /* b_len = 3: permutations of rem taken 3 */
                    for (int q0 = 0; q0 < rem_count; q0++) {
                        for (int q1 = 0; q1 < rem_count; q1++) {
                            if (q1 == q0) continue;
                            for (int q2 = 0; q2 < rem_count; q2++) {
                                if (q2 == q0 || q2 == q1) continue;
                                int b_val = digits[rem[q0]] * 100
                                          + digits[rem[q1]] * 10
                                          + digits[rem[q2]];
                                int c_val = a_val * b_val;
                                if (is_nine_pandigital(a_val, b_val, c_val)) {
                                    set_add(c_val);
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    long long total = 0;
    for (int i = 0; i < product_count; i++) {
        total += products[i];
    }
    return total;
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