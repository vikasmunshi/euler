/* Solution to Euler Problem 15: Lattice Paths. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

/* Big integer arithmetic using base-10^9 limbs (little-endian) */
#define BASE 1000000000ULL
#define MAXLIMBS 64

typedef struct {
    unsigned long long limbs[MAXLIMBS];
    int len;
} BigInt;

static void bi_set(BigInt *a, unsigned long long val) {
    memset(a->limbs, 0, sizeof(a->limbs));
    a->limbs[0] = val % BASE;
    a->limbs[1] = val / BASE;
    a->len = (a->limbs[1] > 0) ? 2 : 1;
}

static void bi_mul_ll(BigInt *a, unsigned long long x) {
    unsigned long long carry = 0;
    for (int i = 0; i < a->len; i++) {
        unsigned long long cur = a->limbs[i] * x + carry;
        a->limbs[i] = cur % BASE;
        carry = cur / BASE;
    }
    while (carry > 0) {
        if (a->len >= MAXLIMBS) { fprintf(stderr, "BigInt overflow in mul\n"); exit(1); }
        a->limbs[a->len] = carry % BASE;
        carry /= BASE;
        a->len++;
    }
}

static void bi_div_ll(BigInt *a, unsigned long long x) {
    unsigned long long rem = 0;
    for (int i = a->len - 1; i >= 0; i--) {
        unsigned long long cur = rem * BASE + a->limbs[i];
        a->limbs[i] = cur / x;
        rem = cur % x;
    }
    while (a->len > 1 && a->limbs[a->len - 1] == 0) a->len--;
}

static char *bi_to_str(const BigInt *a) {
    /* Upper bound: len * 9 + 1 */
    int bufsize = a->len * 9 + 2;
    char *buf = malloc((size_t)bufsize);
    if (!buf) { fprintf(stderr, "OOM\n"); exit(1); }
    int pos = 0;
    /* Print most significant limb without leading zeros */
    pos += sprintf(buf + pos, "%llu", a->limbs[a->len - 1]);
    /* Remaining limbs with leading zeros */
    for (int i = a->len - 2; i >= 0; i--) {
        pos += sprintf(buf + pos, "%09llu", a->limbs[i]);
    }
    buf[pos] = '\0';
    return buf;
}

char *solve(int argc, char *argv[]) {
    int n = atoi(argv[1]);
    /* C(2n, n) = product_{i=1}^{n} (n + i) / i */
    BigInt result;
    bi_set(&result, 1ULL);
    for (int i = 1; i <= n; i++) {
        bi_mul_ll(&result, (unsigned long long)(n + i));
        bi_div_ll(&result, (unsigned long long)i);
    }
    return bi_to_str(&result);
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

    for (int r = 0; r < runs; r++) {
        struct timespec t0, t1;
        clock_gettime(CLOCK_MONOTONIC, &t0);
        char *cur = solve(solve_argc, solve_argv);
        clock_gettime(CLOCK_MONOTONIC, &t1);
        total += (double)(t1.tv_sec - t0.tv_sec)
               + (double)(t1.tv_nsec - t0.tv_nsec) * 1e-9;
        if (result) {
            if (strcmp(cur, result) != 0) {
                fprintf(stderr, "Expected consistent result, got %s previous result=%s\n",
                        cur, result);
                rc = 1;
            }
            free(cur);
        } else {
            result = cur;
        }
    }

    printf("%d %.17g %s\n", runs, total / (double)runs, result ? result : "");
    free(result);
    free(solve_argv);
    return rc;
}