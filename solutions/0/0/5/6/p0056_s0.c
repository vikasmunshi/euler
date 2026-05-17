/* Solution to Euler Problem 56: Powerful Digit Sum. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

/* Big integer represented as array of digits (base 10), little-endian */
typedef struct {
    int *digits;
    int len;
    int cap;
} BigInt;

static BigInt *bigint_new(int cap) {
    BigInt *b = malloc(sizeof(BigInt));
    b->cap = cap;
    b->len = 1;
    b->digits = calloc((size_t)cap, sizeof(int));
    b->digits[0] = 0;
    return b;
}

static void bigint_free(BigInt *b) {
    free(b->digits);
    free(b);
}

/* Set big integer to a small value */
static void bigint_set(BigInt *b, int val) {
    memset(b->digits, 0, (size_t)b->cap * sizeof(int));
    b->len = 0;
    while (val > 0) {
        b->digits[b->len++] = val % 10;
        val /= 10;
    }
    if (b->len == 0) {
        b->len = 1;
        b->digits[0] = 0;
    }
}

/* Multiply big integer by a small integer, result stored in b */
static void bigint_mul_int(BigInt *b, int m) {
    long long carry = 0;
    for (int i = 0; i < b->len; i++) {
        long long prod = (long long)b->digits[i] * m + carry;
        b->digits[i] = (int)(prod % 10);
        carry = prod / 10;
    }
    while (carry > 0) {
        if (b->len >= b->cap) {
            b->cap *= 2;
            b->digits = realloc(b->digits, (size_t)b->cap * sizeof(int));
        }
        b->digits[b->len++] = (int)(carry % 10);
        carry /= 10;
    }
}

/* Compute digit sum of big integer */
static long long bigint_digit_sum(BigInt *b) {
    long long s = 0;
    for (int i = 0; i < b->len; i++) {
        s += b->digits[i];
    }
    return s;
}

long long solve(int argc, char *argv[]) {
    int num_digits = atoi(argv[1]);

    /* stop_at = 10^num_digits */
    int stop_at = 1;
    for (int i = 0; i < num_digits; i++) stop_at *= 10;

    int base_start = stop_at - 100;
    if (base_start < 1) base_start = 1;
    int exp_start = stop_at - 10;
    if (exp_start < 1) exp_start = 1;

    /* Estimate max digits needed: base=99, exp=999...
     * digits ~ exp * log10(base) + 2
     * For num_digits=3: ~999 * 2 + 10 = ~2008 */
    int max_exp = stop_at - 1;
    int max_base = stop_at - 1;
    /* max digits ~ max_exp * ceil(log10(max_base)) + 10 */
    /* Use a safe upper bound */
    int max_digits = max_exp * (num_digits + 1) + 100;
    if (max_digits < 300) max_digits = 300;

    BigInt *b = bigint_new(max_digits);
    long long best = 0;

    for (int base = base_start; base < stop_at; base++) {
        /* Compute base^exp for exp in [exp_start, stop_at) */
        /* First compute base^exp_start */
        bigint_set(b, 1);
        for (int e = 0; e < exp_start; e++) {
            bigint_mul_int(b, base);
        }
        long long ds = bigint_digit_sum(b);
        if (ds > best) best = ds;

        for (int exp = exp_start + 1; exp < stop_at; exp++) {
            bigint_mul_int(b, base);
            ds = bigint_digit_sum(b);
            if (ds > best) best = ds;
        }
    }

    bigint_free(b);
    return best;
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