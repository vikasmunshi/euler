/* Solution to Euler Problem 93: Arithmetic Expressions. */
#include "runner.h"
#include <math.h>

/* Mirrors the Python sibling but without memoisation: the search over four
   numbers is small enough that plain recursion is fast. Values flow as doubles
   and integrality is tested only at the output stage. */

/* A dynamic set of doubles: growable array with linear-scan deduplication. */
typedef struct {
    double *data;
    int size;
    int capacity;
} DoubleSet;

/* Initialise an empty set with a small starting capacity. */
static void ds_init(DoubleSet *s) {
    s->capacity = 64;
    s->size = 0;
    s->data = malloc((size_t)s->capacity * sizeof(double));
}

/* Release the backing array and reset the set to empty. */
static void ds_free(DoubleSet *s) {
    free(s->data);
    s->data = NULL;
    s->size = 0;
    s->capacity = 0;
}

/* Insert v, skipping non-finite values and duplicates; grow on demand. */
static void ds_add(DoubleSet *s, double v) {
    /* Discard NaN/inf produced by degenerate operations. */
    if (!isfinite(v)) return;
    /* Exact equality is fine: we control the operations that produce these. */
    for (int i = 0; i < s->size; i++) {
        if (s->data[i] == v) return;
    }
    if (s->size == s->capacity) {
        s->capacity *= 2;
        s->data = realloc(s->data, (size_t)s->capacity * sizeof(double));
    }
    s->data[s->size++] = v;
}

/* Add every element of src into dst (deduplicated by ds_add). */
static void ds_merge(DoubleSet *dst, const DoubleSet *src) {
    for (int i = 0; i < src->size; i++) {
        ds_add(dst, src->data[i]);
    }
}

/* Collect all values reachable from n doubles by repeated pairwise combination:
   pick every unordered pair, apply each operation, and recurse on the reduced pool. */
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

/* Recursive pool reduction enumerates every parenthesisation/operator choice; pick the
   digit set a<b<c<d with the longest consecutive run 1..n; O(1) over the fixed 126 sets. */
const char *solve(int argc, char *argv[]) {
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
                    /* Use a boolean presence array up to a safe bound */
                    int found[2048] = {0};
                    for (int i = 0; i < results.size; i++) {
                        double v = results.data[i];
                        if (v > 0.0 && v < 2048.0) {
                            /* Round and confirm integrality within a small epsilon. */
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