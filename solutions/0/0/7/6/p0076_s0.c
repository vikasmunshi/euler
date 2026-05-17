/* Solution to Euler Problem 76: Counting Summations. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

/* Big integer using base 10^9 limbs, little-endian */
#define BASE 1000000000LL
#define MAX_LIMBS 16

typedef struct {
    long long limbs[MAX_LIMBS];
    int n; /* number of limbs used */
} BigInt;

static void bigint_set(BigInt *a, long long val) {
    memset(a->limbs, 0, sizeof(a->limbs));
    a->n = 0;
    if (val == 0) { a->n = 1; return; }
    while (val > 0) {
        a->limbs[a->n++] = val % BASE;
        val /= BASE;
    }
}

static void bigint_add(BigInt *result, const BigInt *a, const BigInt *b) {
    long long carry = 0;
    int maxn = (a->n > b->n) ? a->n : b->n;
    result->n = 0;
    for (int i = 0; i < maxn || carry; i++) {
        long long sum = carry;
        if (i < a->n) sum += a->limbs[i];
        if (i < b->n) sum += b->limbs[i];
        result->limbs[i] = sum % BASE;
        carry = sum / BASE;
        result->n = i + 1;
    }
}

static void bigint_sub(BigInt *result, const BigInt *a, const BigInt *b) {
    /* a >= b assumed */
    long long borrow = 0;
    result->n = a->n;
    for (int i = 0; i < a->n; i++) {
        long long diff = a->limbs[i] - borrow - (i < b->n ? b->limbs[i] : 0);
        if (diff < 0) { diff += BASE; borrow = 1; }
        else borrow = 0;
        result->limbs[i] = diff;
    }
    while (result->n > 1 && result->limbs[result->n - 1] == 0) result->n--;
}

static int bigint_is_zero(const BigInt *a) {
    return a->n == 1 && a->limbs[0] == 0;
}

static void bigint_print(const BigInt *a) {
    printf("%lld", a->limbs[a->n - 1]);
    for (int i = a->n - 2; i >= 0; i--) {
        printf("%09lld", a->limbs[i]);
    }
}

/* Pentagonal number g(k) = k*(3k-1)/2 for integer k (positive or negative) */
static long long pentagonal(int k) {
    return (long long)k * (3 * k - 1) / 2;
}

static char *solve(int argc, char *argv[]) {
    int num = (argc > 1) ? atoi(argv[1]) : 100;

    /* p[i] = number of partitions of i */
    BigInt *p = calloc((size_t)(num + 1), sizeof(BigInt));
    if (!p) { fprintf(stderr, "out of memory\n"); return NULL; }

    bigint_set(&p[0], 1);

    for (int n = 1; n <= num; n++) {
        bigint_set(&p[n], 0);
        for (int k = 1; ; k++) {
            long long g_pos = pentagonal(k);
            long long g_neg = pentagonal(-k);
            int done_pos = (g_pos > n);
            int done_neg = (g_neg > n);

            BigInt tmp, tmp2;
            bigint_set(&tmp, 0);
            bigint_set(&tmp2, 0);

            if (!done_pos) bigint_add(&tmp, &tmp, &p[n - (int)g_pos]);
            if (!done_neg) bigint_add(&tmp2, &tmp2, &p[n - (int)g_neg]);

            /* combined = tmp + tmp2 */
            BigInt combined;
            bigint_add(&combined, &tmp, &tmp2);

            if (k % 2 == 1) {
                /* add combined to p[n] */
                BigInt res;
                bigint_add(&res, &p[n], &combined);
                p[n] = res;
            } else {
                /* subtract combined from p[n] */
                BigInt res;
                bigint_sub(&res, &p[n], &combined);
                p[n] = res;
            }

            if (done_pos && done_neg) break;
        }
    }

    /* answer = p[num] - 1 */
    BigInt one, answer;
    bigint_set(&one, 1);
    bigint_sub(&answer, &p[num], &one);

    /* Format answer as string */
    /* Compute length needed */
    int len = 0;
    char *buf = malloc(MAX_LIMBS * 10 + 2);
    if (!buf) { free(p); return NULL; }
    char tmp_buf[32];
    len = snprintf(tmp_buf, sizeof(tmp_buf), "%lld", answer.limbs[answer.n - 1]);
    strcpy(buf, tmp_buf);
    for (int i = answer.n - 2; i >= 0; i--) {
        char seg[16];
        snprintf(seg, sizeof(seg), "%09lld", answer.limbs[i]);
        strcat(buf, seg);
    }

    free(p);
    return buf;
}

/* Usage: ./file <kwarg>... [--runs=1] [--show]
 * Output: "<runs> <avg_seconds> <result>" */
int main(int argc, char *argv[]) {
    int runs = 1;

    char **solve_argv = malloc((size_t)argc * sizeof(char *));
    if (!solve_argv) { fprintf(stderr, "runner: out of memory\n"); return 1; }
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

    for (int r = 0; r < runs; r++) {
        struct timespec t0, t1;
        clock_gettime(CLOCK_MONOTONIC, &t0);
        char *cur = solve(solve_argc, solve_argv);
        clock_gettime(CLOCK_MONOTONIC, &t1);
        total += (double)(t1.tv_sec - t0.tv_sec)
               + (double)(t1.tv_nsec - t0.tv_nsec) * 1e-9;
        if (result) {
            if (cur && strcmp(cur, result) != 0) {
                fprintf(stderr, "Inconsistent results: %s vs %s\n", cur, result);
                rc = 1;
            }
            free(result);
        }
        result = cur;
    }

    free(solve_argv);
    printf("%d %.17g %s\n", runs, total / (double)runs, result ? result : "NULL");
    free(result);
    return rc;
}