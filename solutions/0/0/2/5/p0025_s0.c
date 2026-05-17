/* Solution to Euler Problem 25: $1000$-digit Fibonacci Number. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

/*
 * Big-integer addition using arrays of decimal digits (base 10^9 limbs).
 * Each limb stores up to 9 decimal digits.
 */

#define BASE      1000000000ULL
#define MAX_LIMBS 200  /* 200 * 9 = 1800 digits, more than enough */

typedef struct {
    unsigned long long limbs[MAX_LIMBS];
    int len;
} BigInt;

static void bigint_set_one(BigInt *a) {
    memset(a->limbs, 0, sizeof(a->limbs));
    a->limbs[0] = 1;
    a->len = 1;
}

/* dst = a + b */
static void bigint_add(BigInt *dst, const BigInt *a, const BigInt *b) {
    int maxlen = a->len > b->len ? a->len : b->len;
    unsigned long long carry = 0;
    int i;
    for (i = 0; i < maxlen || carry; i++) {
        unsigned long long sum = carry;
        if (i < a->len) sum += a->limbs[i];
        if (i < b->len) sum += b->limbs[i];
        dst->limbs[i] = sum % BASE;
        carry = sum / BASE;
    }
    dst->len = i;
}

/* Return total decimal digit count of a */
static int bigint_digit_count(const BigInt *a) {
    if (a->len == 0) return 1;
    /* count digits in the top limb */
    unsigned long long top = a->limbs[a->len - 1];
    int d = 0;
    while (top > 0) { top /= 10; d++; }
    if (d == 0) d = 1;
    return d + (a->len - 1) * 9;
}

long long solve(int argc, char *argv[]) {
    int n = (argc >= 2) ? atoi(argv[1]) : 1000;

    BigInt a, b, tmp;
    bigint_set_one(&a);
    bigint_set_one(&b);

    long long i = 2;
    while (bigint_digit_count(&b) < n) {
        /* tmp = a + b */
        bigint_add(&tmp, &a, &b);
        /* a = b */
        memcpy(&a, &b, sizeof(BigInt));
        /* b = tmp */
        memcpy(&b, &tmp, sizeof(BigInt));
        i++;
    }
    return i;
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