/* Solution to Euler Problem 93: Arithmetic Expressions. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <time.h>

/* We store sets of reachable double values.
   Since the memoization in Python relies on sorted tuples as cache keys,
   we implement the recursion directly without memoization in C
   (the problem is small enough). */

/* A dynamic set of doubles */
typedef struct {
    double *data;
    int size;
    int capacity;
} DoubleSet;

static void ds_init(DoubleSet *s) {
    s->capacity = 64;
    s->size = 0;
    s->data = malloc((size_t)s->capacity * sizeof(double));
}

static void ds_free(DoubleSet *s) {
    free(s->data);
    s->data = NULL;
    s->size = 0;
    s->capacity = 0;
}

static void ds_add(DoubleSet *s, double v) {
    /* Check for NaN or inf */
    if (!isfinite(v)) return;
    /* Check duplicate (with exact equality since we control the operations) */
    for (int i = 0; i < s->size; i++) {
        if (s->data[i] == v) return;
    }
    if (s->size == s->capacity) {
        s->capacity *= 2;
        s->data = realloc(s->data, (size_t)s->capacity * sizeof(double));
    }
    s->data[s->size++] = v;
}

static void ds_merge(DoubleSet *dst, const DoubleSet *src) {
    for (int i = 0; i < src->size; i++) {
        ds_add(dst, src->data[i]);
    }
}

/* Recursive function: given an array of 'n' doubles, compute all reachable values */
static void eval_all(double *vals, int n, DoubleSet *out) {
    if (n == 1) {
        ds_add(out, vals[0]);
        return;
    }

    /* Try every unordered pair (i, j) */
    double rest[4];
    double combined[5]; /* rest + new value */

    for (int i = 0; i < n - 1; i++) {
        for (int j = i + 1; j < n; j++) {
            double a = vals[i];
            double b = vals[j];

            /* Build rest array */
            int rlen = 0;
            for (int k = 0; k < n; k++) {
                if (k != i && k != j) {
                    rest[rlen++] = vals[k];
                }
            }

            /* 5 operations: a+b, |a-b|, a*b, a/b (if b!=0), b/a (if a!=0) */
            double ops[5];
            int nops = 0;
            ops[nops++] = a + b;
            ops[nops++] = fabs(a - b);
            ops[nops++] = a * b;
            if (b != 0.0) ops[nops++] = a / b;
            if (a != 0.0) ops[nops++] = b / a;

            for (int op = 0; op < nops; op++) {
                /* Build new vals = rest + ops[op] */
                memcpy(combined, rest, (size_t)rlen * sizeof(double));
                combined[rlen] = ops[op];
                eval_all(combined, rlen + 1, out);
            }
        }
    }
}

char *solve(int argc, char *argv[]) {
    (void)argc;
    (void)argv;

    char best_digits[5] = "";
    int best_length = 0;

    for (int a = 1; a <= 6; a++) {
        for (int b = a + 1; b <= 7; b++) {
            for (int c = b + 1; c <= 8; c++) {
                for (int d = c + 1; d <= 9; d++) {
                    double vals[4] = {(double)a, (double)b, (double)c, (double)d};

                    DoubleSet results;
                    ds_init(&results);
                    eval_all(vals, 4, &results);

                    /* Find positive integers in results */
                    /* Use a boolean array up to some max */
                    int found[2048] = {0};
                    for (int i = 0; i < results.size; i++) {
                        double v = results.data[i];
                        if (v > 0.0 && v < 2048.0) {
                            /* Check if integer */
                            double rounded = floor(v + 0.5);
                            if (fabs(v - rounded) < 1e-9) {
                                int iv = (int)rounded;
                                if (iv >= 1 && iv < 2048) {
                                    found[iv] = 1;
                                }
                            }
                        }
                    }
                    ds_free(&results);

                    /* Find consecutive run from 1 */
                    int length = 0;
                    while (length + 1 < 2048 && found[length + 1]) {
                        length++;
                    }

                    if (length > best_length) {
                        best_length = length;
                        snprintf(best_digits, sizeof(best_digits), "%d%d%d%d", a, b, c, d);
                    }
                }
            }
        }
    }

    char *result = malloc(5);
    if (!result) return NULL;
    strncpy(result, best_digits, 5);
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

    char *result = NULL;
    double total = 0.0;
    int rc = 0;
    char *prev_result = NULL;

    for (int r = 0; r < runs; r++) {
        struct timespec t0, t1;
        clock_gettime(CLOCK_MONOTONIC, &t0);
        char *cur = solve(solve_argc, solve_argv);
        clock_gettime(CLOCK_MONOTONIC, &t1);
        total += (double)(t1.tv_sec - t0.tv_sec)
               + (double)(t1.tv_nsec - t0.tv_nsec) * 1e-9;
        if (prev_result && cur && strcmp(cur, prev_result) != 0) {
            fprintf(stderr, "Expected consistent result, got %s previous result=%s\n",
                    cur, prev_result);
            rc = 1;
        }
        if (prev_result) free(prev_result);
        prev_result = cur;
        result = cur;
    }

    printf("%d %.17g %s\n", runs, total / (double)runs, result ? result : "");

    if (result) free(result);
    free(solve_argv);
    return rc;
}