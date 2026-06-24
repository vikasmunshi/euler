/* Solution to Euler Problem 5: Smallest Multiple. */
#include "runner.h"

/* Big integer as array of uint32 limbs, little-endian base 2^32 */
#define MAX_LIMBS 64

typedef struct {
    unsigned int limbs[MAX_LIMBS];
    int n; /* number of limbs in use */
} BigInt;

static void bi_set_ll(BigInt *a, unsigned long long val) {
    memset(a->limbs, 0, sizeof(a->limbs));
    a->limbs[0] = (unsigned int)(val & 0xFFFFFFFFULL);
    a->limbs[1] = (unsigned int)(val >> 32);
    a->n = (a->limbs[1] != 0) ? 2 : 1;
}

static void bi_copy(BigInt *dst, const BigInt *src) {
    memcpy(dst->limbs, src->limbs, sizeof(src->limbs));
    dst->n = src->n;
}

/* a = a / small, return remainder */
static unsigned long long bi_div_small(BigInt *a, unsigned long long d) {
    unsigned long long rem = 0;
    for (int i = a->n - 1; i >= 0; i--) {
        unsigned long long cur = (rem << 32) | (unsigned long long)a->limbs[i];
        a->limbs[i] = (unsigned int)(cur / d);
        rem = cur % d;
    }
    while (a->n > 1 && a->limbs[a->n - 1] == 0) a->n--;
    return rem;
}

/* a = a * small */
static void bi_mul_small(BigInt *a, unsigned long long m) {
    unsigned long long carry = 0;
    for (int i = 0; i < a->n; i++) {
        unsigned long long cur = (unsigned long long)a->limbs[i] * m + carry;
        a->limbs[i] = (unsigned int)(cur & 0xFFFFFFFFULL);
        carry = cur >> 32;
    }
    while (carry) {
        if (a->n >= MAX_LIMBS) break;
        a->limbs[a->n] = (unsigned int)(carry & 0xFFFFFFFFULL);
        carry >>= 32;
        a->n++;
    }
}

/* gcd of two long long values */
static long long gcd_ll(long long a, long long b) {
    while (b) {
        long long t = b;
        b = a % b;
        a = t;
    }
    return a;
}

/*
 * Compute lcm(result, y) where result is BigInt and y is long long.
 * lcm(a, b) = a / gcd(a, b) * b
 * gcd(BigInt, y): since y fits in long long, gcd(a, y) = gcd(a mod y, y)
 */
static void bi_lcm_small(BigInt *result, long long y) {
    /* compute a mod y to get gcd */
    BigInt tmp;
    bi_copy(&tmp, result);
    long long rem = (long long)bi_div_small(&tmp, (unsigned long long)y);
    long long g = gcd_ll(rem < 0 ? -rem : rem, y);
    /* result = result / g * y */
    bi_div_small(result, (unsigned long long)g);
    bi_mul_small(result, (unsigned long long)y);
}

/* Print BigInt as decimal string */
static void bi_print(const BigInt *a) {
    /* convert to decimal by repeated division by 10 */
    char buf[256];
    int pos = 0;
    BigInt tmp;
    bi_copy(&tmp, a);
    /* check if zero */
    int all_zero = 1;
    for (int i = 0; i < tmp.n; i++) if (tmp.limbs[i]) { all_zero = 0; break; }
    if (all_zero) { printf("0"); return; }
    while (1) {
        int nonzero = 0;
        for (int i = 0; i < tmp.n; i++) if (tmp.limbs[i]) { nonzero = 1; break; }
        if (!nonzero) break;
        unsigned long long rem = bi_div_small(&tmp, 10ULL);
        buf[pos++] = (char)('0' + (int)rem);
    }
    for (int i = pos - 1; i >= 0; i--) putchar(buf[i]);
}

/* Return decimal string of BigInt (heap allocated) */
static char *bi_to_str(const BigInt *a) {
    char buf[256];
    int pos = 0;
    BigInt tmp;
    bi_copy(&tmp, a);
    int all_zero = 1;
    for (int i = 0; i < tmp.n; i++) if (tmp.limbs[i]) { all_zero = 0; break; }
    if (all_zero) {
        char *s = malloc(2);
        s[0] = '0'; s[1] = '\0';
        return s;
    }
    while (1) {
        int nonzero = 0;
        for (int i = 0; i < tmp.n; i++) if (tmp.limbs[i]) { nonzero = 1; break; }
        if (!nonzero) break;
        unsigned long long rem = bi_div_small(&tmp, 10ULL);
        buf[pos++] = (char)('0' + (int)rem);
    }
    char *s = malloc((size_t)(pos + 1));
    for (int i = 0; i < pos; i++) s[i] = buf[pos - 1 - i];
    s[pos] = '\0';
    return s;
}

/*
 * Iterative LCM of 1..n: fold a running BigInt result with lcm(result, y) for y = 2..n,
 * each step using lcm = result / gcd * y on a hand-rolled big integer; O(n log n).
 */
const char *solve(int argc, char *argv[]) {
    int n = parse_int(argv[1]);
    BigInt result;
    bi_set_ll(&result, 1ULL);
    for (int y = 2; y <= n; y++) {
        bi_lcm_small(&result, (long long)y);
    }
    return bi_to_str(&result);
}
