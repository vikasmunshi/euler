/* Solution to Euler Problem 80: Square Root Digital Expansion. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <time.h>

#define BASE     1000000000ULL
#define MAXLIMBS 64

typedef unsigned long long ull;
typedef __uint128_t u128;

typedef struct { ull limbs[MAXLIMBS]; int size; } BigInt;

static void bi_zero(BigInt *a) {
    memset(a->limbs, 0, sizeof(a->limbs));
    a->size = 1;
}

static void bi_from_ull(BigInt *a, ull v) {
    bi_zero(a);
    a->limbs[0] = v % BASE;
    if (v >= BASE) { a->limbs[1] = v / BASE; a->size = 2; }
}

static void bi_copy(BigInt *dst, const BigInt *src) {
    memcpy(dst, src, sizeof(BigInt));
}

static void bi_trim(BigInt *a) {
    while (a->size > 1 && a->limbs[a->size-1] == 0) a->size--;
}

static int bi_cmp(const BigInt *a, const BigInt *b) {
    if (a->size != b->size) return a->size > b->size ? 1 : -1;
    for (int i = a->size-1; i >= 0; i--) {
        if (a->limbs[i] > b->limbs[i]) return  1;
        if (a->limbs[i] < b->limbs[i]) return -1;
    }
    return 0;
}

/* Returns 1 if a - b == 1, i.e. a == b+1 */
static int bi_diff_is_one(const BigInt *a, const BigInt *b) {
    /* compute a - b and check if result == 1 */
    if (a->size < b->size) return 0;
    if (bi_cmp(a, b) <= 0) return 0;
    /* subtract */
    ull limbs[MAXLIMBS];
    long long borrow = 0;
    int n = a->size;
    for (int i = 0; i < n; i++) {
        long long d = (long long)a->limbs[i]
                    - (i < b->size ? (long long)b->limbs[i] : 0LL) - borrow;
        if (d < 0) { d += (long long)BASE; borrow = 1; } else borrow = 0;
        limbs[i] = (ull)d;
    }
    /* check if result == 1 */
    if (limbs[0] != 1) return 0;
    for (int i = 1; i < n; i++) if (limbs[i] != 0) return 0;
    return 1;
}

static void bi_add(BigInt *dst, const BigInt *a, const BigInt *b) {
    int n = a->size > b->size ? a->size : b->size;
    ull carry = 0;
    int i;
    for (i = 0; i < n || carry; i++) {
        ull s = carry + (i < a->size ? a->limbs[i] : 0)
                      + (i < b->size ? b->limbs[i] : 0);
        if (i < MAXLIMBS) dst->limbs[i] = s % BASE;
        carry = s / BASE;
        if (i >= n) n++;
    }
    dst->size = n < MAXLIMBS ? n : MAXLIMBS;
    bi_trim(dst);
}

static void bi_div2(BigInt *dst, const BigInt *a) {
    bi_copy(dst, a);
    ull carry = 0;
    for (int i = dst->size-1; i >= 0; i--) {
        ull cur = dst->limbs[i] + carry * BASE;
        dst->limbs[i] = cur / 2;
        carry = cur & 1ULL;
    }
    bi_trim(dst);
}

static void bi_mul(BigInt *dst, const BigInt *a, const BigInt *b) {
    BigInt t;
    memset(&t, 0, sizeof(t));
    t.size = (a->size + b->size < MAXLIMBS) ? a->size + b->size : MAXLIMBS;
    for (int i = 0; i < a->size; i++) {
        ull carry = 0;
        for (int j = 0; j < b->size && i+j < MAXLIMBS; j++) {
            ull cur = t.limbs[i+j] + a->limbs[i] * b->limbs[j] + carry;
            t.limbs[i+j] = cur % BASE;
            carry = cur / BASE;
        }
        if (i + b->size < MAXLIMBS) t.limbs[i + b->size] += carry;
    }
    bi_trim(&t);
    bi_copy(dst, &t);
}

static void bi_mul_limb(BigInt *dst, const BigInt *a, ull v) {
    ull carry = 0;
    int n = a->size;
    for (int i = 0; i < n; i++) {
        ull cur = a->limbs[i] * v + carry;
        dst->limbs[i] = cur % BASE;
        carry = cur / BASE;
    }
    if (carry && n < MAXLIMBS) { dst->limbs[n] = carry; n++; }
    dst->size = n;
    bi_trim(dst);
}

static void bi_pow10(BigInt *a, int exp) {
    bi_from_ull(a, 1);
    BigInt t;
    ull base9 = 1000000000ULL;
    int chunks = exp / 9, rem = exp % 9;
    ull baserem = 1;
    for (int i = 0; i < rem; i++) baserem *= 10;
    for (int i = 0; i < chunks; i++) { bi_mul_limb(&t, a, base9); bi_copy(a, &t); }
    if (baserem > 1) { bi_mul_limb(&t, a, baserem); bi_copy(a, &t); }
}

/* Convert to decimal string; caller frees */
static char *bi_to_str(const BigInt *a) {
    char *buf = malloc((size_t)(a->size * 9 + 4));
    if (!buf) return NULL;
    int pos = sprintf(buf, "%llu", a->limbs[a->size-1]);
    for (int i = a->size-2; i >= 0; i--)
        pos += sprintf(buf + pos, "%09llu", a->limbs[i]);
    return buf;
}

static int is_perfect_square(int n) {
    int s = (int)(sqrt((double)n) + 0.5);
    for (int k = s-1; k <= s+1; k++)
        if (k > 0 && k * k == n) return 1;
    return 0;
}

/*
 * Binary search integer square root:
 * Find floor(sqrt(n * 10^(2*digits))).
 * Maintain low*low <= scaled_number < high*high.
 * When high - low == 1, low is the answer.
 */
static int sqrt_digit_sum_binary_search(int n, int digits) {
    /* scaled_number = n * 10^(2*digits) */
    BigInt scale;
    bi_pow10(&scale, 2 * digits);

    BigInt scaled_number;
    bi_from_ull(&scaled_number, (ull)n);
    { BigInt t; bi_mul(&t, &scaled_number, &scale); bi_copy(&scaled_number, &t); }

    /* low = 0, high = scaled_number */
    BigInt low, high;
    bi_from_ull(&low, 0);
    bi_copy(&high, &scaled_number);

    /* Binary search: while high - low > 1 */
    for (;;) {
        /* Check if high - low <= 1 */
        if (bi_cmp(&high, &low) <= 0) break;
        if (bi_diff_is_one(&high, &low)) break;

        /* mid = (low + high) // 2 */
        BigInt sum_lh, mid;
        bi_add(&sum_lh, &low, &high);
        bi_div2(&mid, &sum_lh);

        /* if mid*mid <= scaled_number: low = mid else high = mid */
        BigInt mid_sq;
        bi_mul(&mid_sq, &mid, &mid);

        if (bi_cmp(&mid_sq, &scaled_number) <= 0) {
            bi_copy(&low, &mid);
        } else {
            bi_copy(&high, &mid);
        }
    }

    /* low is floor(sqrt(scaled_number)) */
    char *str = bi_to_str(&low);
    if (!str) return 0;
    int sum = 0;
    int len = (int)strlen(str);
    int take = len < digits ? len : digits;
    for (int i = 0; i < take; i++) sum += str[i] - '0';
    free(str);
    return sum;
}

long long solve(int argc, char *argv[]) {
    int digits  = atoi(argv[1]);
    int max_num = atoi(argv[2]);
    long long result = 0;
    for (int i = 2; i <= max_num; i++) {
        if (is_perfect_square(i)) continue;
        result += sqrt_digit_sum_binary_search(i, digits);
    }
    return result;
}

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

    long long result = 0;
    double total = 0.0;
    int rc = 0, has_result = 0;

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