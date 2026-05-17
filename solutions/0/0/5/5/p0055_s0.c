/* Solution to Euler Problem 55: Lychrel Numbers. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

/* Big number represented as array of digits (base 10), little-endian */
#define MAX_DIGITS 128

typedef struct {
    int digits[MAX_DIGITS];
    int len;
} BigNum;

static void bignum_from_ll(BigNum *b, long long n) {
    b->len = 0;
    if (n == 0) {
        b->digits[0] = 0;
        b->len = 1;
        return;
    }
    while (n > 0) {
        b->digits[b->len++] = (int)(n % 10);
        n /= 10;
    }
}

static void bignum_add_reverse(BigNum *result, const BigNum *a) {
    /* result = a + reverse(a) */
    int carry = 0;
    int n = a->len;
    result->len = n;
    for (int i = 0; i < n; i++) {
        int sum = a->digits[i] + a->digits[n - 1 - i] + carry;
        result->digits[i] = sum % 10;
        carry = sum / 10;
    }
    if (carry) {
        result->digits[result->len++] = carry;
    }
}

static int bignum_is_palindrome(const BigNum *b) {
    int n = b->len;
    for (int i = 0; i < n / 2; i++) {
        if (b->digits[i] != b->digits[n - 1 - i])
            return 0;
    }
    return 1;
}

static int is_lychrel(long long number, int max_iterations) {
    BigNum a, result;
    bignum_from_ll(&a, number);

    for (int iter = 0; iter < max_iterations; iter++) {
        bignum_add_reverse(&result, &a);
        if (bignum_is_palindrome(&result))
            return 0;
        a = result;
    }
    return 1;
}

long long solve(int argc, char *argv[]) {
    int max_iterations = atoi(argv[1]);
    int max_limit = atoi(argv[2]);

    long long count = 0;
    for (int i = 1; i <= max_limit; i++) {
        if (is_lychrel((long long)i, max_iterations))
            count++;
    }
    return count;
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