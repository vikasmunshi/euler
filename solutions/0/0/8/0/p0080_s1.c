/* Solution to Euler Problem 80: Square Root Digital Expansion. */
#include "runner.h"
#include <math.h>

#define BASE     1000000000ULL
#define MAXLIMBS 64

typedef unsigned long long ull;
typedef __uint128_t u128;

typedef struct { ull limbs[MAXLIMBS]; int size; } BigInt;

/* Set a to zero (canonical one-limb form). */
static void bi_zero(BigInt *a) {
    memset(a->limbs, 0, sizeof(a->limbs));
    a->size = 1;
}

/* Initialize a from a 64-bit value, splitting into at most two base-10^9 limbs. */
static void bi_from_ull(BigInt *a, ull v) {
    bi_zero(a);
    a->limbs[0] = v % BASE;
    if (v >= BASE) { a->limbs[1] = v / BASE; a->size = 2; }
}

/* Copy src into dst. */
static void bi_copy(BigInt *dst, const BigInt *src) {
    memcpy(dst, src, sizeof(BigInt));
}

/* Drop leading zero limbs, keeping at least one. */
static void bi_trim(BigInt *a) {
    while (a->size > 1 && a->limbs[a->size-1] == 0) a->size--;
}

/* Compare magnitudes: returns -1, 0, or 1 for a < b, a == b, a > b. */
static int bi_cmp(const BigInt *a, const BigInt *b) {
    if (a->size != b->size) return a->size > b->size ? 1 : -1;
    for (int i = a->size-1; i >= 0; i--) {
        if (a->limbs[i] > b->limbs[i]) return  1;
        if (a->limbs[i] < b->limbs[i]) return -1;
    }
    return 0;
}

/* Test a - b == 1 directly, avoiding a full subtraction allocation in the search loop. */
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

/* dst = a + b with carry propagation across limbs. */
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

/* dst = a / 2, propagating the odd-limb remainder downward as carry. */
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

/* dst = a * b via schoolbook O(size_a * size_b); products fit in u128 per limb pair. */
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

/* dst = a * v for a single-limb multiplier v. */
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

/* a = 10^exp, built by repeated single-limb multiplies (chunks of 9 plus remainder). */
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

/* Convert to decimal string; caller frees. Top limb plain, rest zero-padded to 9 digits. */
static char *bi_to_str(const BigInt *a) {
    char *buf = malloc((size_t)(a->size * 9 + 4));
    if (!buf) return NULL;
    int pos = sprintf(buf, "%llu", a->limbs[a->size-1]);
    for (int i = a->size-2; i >= 0; i--)
        pos += sprintf(buf + pos, "%09llu", a->limbs[i]);
    return buf;
}

/* O(1) test: round sqrt(n) to a double and check the nearby integers exactly. */
static int is_perfect_square(int n) {
    int s = (int)(sqrt((double)n) + 0.5);
    for (int k = s-1; k <= s+1; k++)
        if (k > 0 && k * k == n) return 1;
    return 0;
}

/*
 * Sum the first `digits` decimals of sqrt(n) via floor(sqrt(n * 10^(2*digits))) found by
 * binary search on the invariant low^2 <= scaled < high^2. Only multiplication, never division;
 * linear convergence ~log2(sqrt(scaled)) iterations (~166 for 100 digits).
 */
static int sqrt_digit_sum_binary_search(int n, int digits) {
    /* scaled_number = n * 10^(2*digits) */
    BigInt scale;
    bi_pow10(&scale, 2 * digits);

    BigInt scaled_number;
    bi_from_ull(&scaled_number, (ull)n);
    { BigInt t; bi_mul(&t, &scaled_number, &scale); bi_copy(&scaled_number, &t); }

    /* low = 0, high = scaled_number (a loose but always-valid bracket) */
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

/*
 * Sum digit sums of the first `digits` decimals of every irrational sqrt(i) for i in [2, max_num].
 * Each root uses binary-search integer sqrt of the 10^(2*digits)-scaled value; O(N * d^2).
 */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int digits  = parse_int(argv[1]);
    int max_num = parse_int(argv[2]);
    long long result = 0;
    for (int i = 2; i <= max_num; i++) {
        if (is_perfect_square(i)) continue;
        result += sqrt_digit_sum_binary_search(i, digits);
    }
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(result)); return _answer; }
}