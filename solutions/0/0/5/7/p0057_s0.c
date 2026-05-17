/* Solution to Euler Problem 57: Square Root Convergents. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <stdint.h>

/* Big integer: base 10^9, little-endian limbs */
#define BASE 1000000000ULL
#define MAX_LIMBS 512

typedef struct {
    uint32_t limbs[MAX_LIMBS];
    int size;
} BigInt;

static void bi_set_int(BigInt *a, uint64_t val) {
    memset(a->limbs, 0, sizeof(a->limbs));
    a->size = 0;
    if (val == 0) {
        a->limbs[0] = 0;
        a->size = 1;
        return;
    }
    int i = 0;
    while (val > 0 && i < MAX_LIMBS) {
        a->limbs[i++] = (uint32_t)(val % BASE);
        val /= BASE;
    }
    a->size = i;
}

/* a = b + 2*c */
static void bi_add_twice(BigInt *a, const BigInt *b, const BigInt *c) {
    int n = b->size > c->size ? b->size : c->size;
    uint64_t carry = 0;
    int i;
    for (i = 0; i < n || carry; i++) {
        if (i >= MAX_LIMBS) break;
        uint64_t sum = carry;
        if (i < b->size) sum += b->limbs[i];
        if (i < c->size) sum += 2ULL * c->limbs[i];
        a->limbs[i] = (uint32_t)(sum % BASE);
        carry = sum / BASE;
    }
    a->size = i;
    while (a->size > 1 && a->limbs[a->size - 1] == 0) a->size--;
}

/* a = b + c */
static void bi_add(BigInt *a, const BigInt *b, const BigInt *c) {
    int n = b->size > c->size ? b->size : c->size;
    uint64_t carry = 0;
    int i;
    for (i = 0; i < n || carry; i++) {
        if (i >= MAX_LIMBS) break;
        uint64_t sum = carry;
        if (i < b->size) sum += b->limbs[i];
        if (i < c->size) sum += c->limbs[i];
        a->limbs[i] = (uint32_t)(sum % BASE);
        carry = sum / BASE;
    }
    a->size = i;
    while (a->size > 1 && a->limbs[a->size - 1] == 0) a->size--;
}

/* Count decimal digits */
static int bi_decimal_digits(const BigInt *a) {
    if (a->size == 0) return 1;
    int top = a->size - 1;
    uint32_t top_limb = a->limbs[top];
    int d = top * 9;
    if (top_limb == 0) {
        d += 1;
    } else {
        uint32_t t = top_limb;
        int cnt = 0;
        while (t > 0) { cnt++; t /= 10; }
        d += cnt;
    }
    return d;
}

long long solve(int argc, char *argv[]) {
    int expansions = (argc >= 2) ? atoi(argv[1]) : 1000;

    BigInt num, den, new_num, new_den;
    bi_set_int(&num, 1);
    bi_set_int(&den, 1);

    long long result = 0;

    for (int i = 0; i < expansions; i++) {
        bi_add_twice(&new_num, &num, &den);
        bi_add(&new_den, &num, &den);

        num = new_num;
        den = new_den;

        int dnum = bi_decimal_digits(&num);
        int dden = bi_decimal_digits(&den);
        if (dnum > dden) result++;
    }

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