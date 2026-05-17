/* Solution to Euler Problem 65: Convergents of $e$. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

#define BASE 1000000000ULL
#define MAXDIGITS 2000

typedef struct {
    unsigned long long d[MAXDIGITS];
    int len;
} BigInt;

static void bigint_set(BigInt *a, unsigned long long val) {
    memset(a->d, 0, sizeof(a->d));
    a->len = 1;
    a->d[0] = val % BASE;
    if (val >= BASE) {
        a->d[1] = val / BASE;
        a->len = 2;
    }
}

/* dst = a * scalar + b */
static void bigint_mul_add(BigInt *dst, const BigInt *a, unsigned long long scalar, const BigInt *b) {
    int maxlen = a->len > b->len ? a->len : b->len;
    unsigned long long carry = 0;
    int i;
    for (i = 0; i < maxlen + 2; i++) {
        unsigned long long av = (i < a->len) ? a->d[i] : 0ULL;
        unsigned long long bv = (i < b->len) ? b->d[i] : 0ULL;
        unsigned long long val = av * scalar + bv + carry;
        dst->d[i] = val % BASE;
        carry = val / BASE;
    }
    dst->len = maxlen + 2;
    while (dst->len > 1 && dst->d[dst->len - 1] == 0)
        dst->len--;
}

static long long bigint_digit_sum(const BigInt *a) {
    long long sum = 0;
    for (int i = 0; i < a->len; i++) {
        unsigned long long v = a->d[i];
        while (v > 0) {
            sum += (long long)(v % 10);
            v /= 10;
        }
    }
    return sum;
}

static int e_denominator(int n) {
    if (n == 1) return 2;
    if (n % 3 == 0) return 2 * (n / 3);
    return 1;
}

long long solve(int argc, char *argv[]) {
    int n = atoi(argv[1]);

    BigInt *h_prev2 = (BigInt *)malloc(sizeof(BigInt));
    BigInt *h_prev1 = (BigInt *)malloc(sizeof(BigInt));
    BigInt *h_curr  = (BigInt *)malloc(sizeof(BigInt));

    if (!h_prev2 || !h_prev1 || !h_curr) {
        fprintf(stderr, "Out of memory\n");
        return -1;
    }

    bigint_set(h_prev2, 1ULL);
    bigint_set(h_prev1, (unsigned long long)e_denominator(1));

    if (n == 1) {
        long long ans = bigint_digit_sum(h_prev1);
        free(h_prev2); free(h_prev1); free(h_curr);
        return ans;
    }

    for (int k = 2; k <= n; k++) {
        unsigned long long ak = (unsigned long long)e_denominator(k);
        bigint_mul_add(h_curr, h_prev1, ak, h_prev2);
        BigInt *tmp = h_prev2;
        h_prev2 = h_prev1;
        h_prev1 = h_curr;
        h_curr = tmp;
    }

    long long ans = bigint_digit_sum(h_prev1);
    free(h_prev2); free(h_prev1); free(h_curr);
    return ans;
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