/* Solution to Euler Problem 76: Counting Summations. */
#include "runner.h"

/*
 * Explicit partition enumeration (s2).
 * The Python version has safe_limit=50 and raises OverflowError for n>50.
 * The test framework expects correct answers for n=100 and n=1000 for s2 as well,
 * so we implement the same counting recursion without a hard safe_limit cutoff,
 * since the Python s2 just raises but the C version should return the count.
 * We use big integers to handle large results.
 */

#define BASE 1000000000LL
#define NLIMBS 8

typedef struct {
    long long limbs[NLIMBS];
    int n;
} BI;

/* Set a big integer to zero. */
static void bi_zero(BI *a) {
    memset(a->limbs, 0, sizeof(a->limbs));
    a->n = 1;
}

/* a += b in place with carry propagation, clamped to NLIMBS limbs. */
static void bi_add_inplace(BI *a, const BI *b) {
    long long carry = 0;
    int maxn = (a->n > b->n) ? a->n : b->n;
    for (int i = 0; i < maxn || carry; i++) {
        long long sum = carry;
        if (i < a->n) sum += a->limbs[i];
        else { if (i < NLIMBS) a->limbs[i] = 0; }
        if (i < b->n) sum += b->limbs[i];
        if (i < NLIMBS) { a->limbs[i] = sum % BASE; }
        carry = sum / BASE;
        if (i >= a->n && i < NLIMBS) a->n = i + 1;
    }
    if (a->n < maxn) a->n = maxn;
}

/* a += 1 in place, rippling the carry through full limbs. */
static void bi_inc(BI *a) {
    for (int i = 0; i < NLIMBS; i++) {
        a->limbs[i]++;
        if (a->limbs[i] < BASE) break;
        a->limbs[i] = 0;
        if (i+1 >= a->n) a->n = i+2;
    }
}

/* a -= 1 in place, borrowing through zero limbs. */
static void bi_dec(BI *a) {
    for (int i = 0; i < a->n; i++) {
        if (a->limbs[i] > 0) { a->limbs[i]--; break; }
        a->limbs[i] = BASE - 1;
    }
    while (a->n > 1 && a->limbs[a->n-1] == 0) a->n--;
}

/*
 * Memoized count of partitions: same structure as s2 Python but just counting.
 * count(number, slots): partitions of number into parts <= slots.
 * We use a 2D DP table since s2 Python uses lru_cache (memoization).
 */
static BI *g_dp = NULL;
static int g_num = 0;

/* Address of table cell dp[nb][sl] in the flat (g_num+1)-stride layout. */
static BI *dp_get(int nb, int sl) {
    return &g_dp[nb * (g_num + 1) + sl];
}

/*
 * Explicit partition recurrence count(nb, sl) filled bottom-up, mirroring s2 Python but
 * counting leaves instead of building lists: the leaf [n] increments, deeper partitions add
 * dp[nb-n][min(nb-n, n)]. O(n^2) states with O(n) work each, hence O(n^3); answer is
 * dp[num][num]-1 in base-10^9 big integers.
 */
const char *solve(int argc, char *argv[]) {
    int num = (argc > 1) ? parse_int(argv[1]) : 100;
    g_num = num;

    if (num <= 0) {
        char *buf = malloc(4); strcpy(buf, "0"); return buf;
    }

    size_t sz = (size_t)(num + 1) * (size_t)(num + 1);
    g_dp = calloc(sz, sizeof(BI));
    if (!g_dp) { fprintf(stderr, "out of memory\n"); return NULL; }

    /* Initialize all to n=1 (zero value) */
    for (size_t i = 0; i < sz; i++) g_dp[i].n = 1;

    /* Python: number==1 -> return [[1]], so count=1 for nb=1, sl>=1 */
    for (int sl = 1; sl <= num; sl++) {
        dp_get(1, sl)->limbs[0] = 1;
        dp_get(1, sl)->n = 1;
    }

    /* Fill nb=2..num */
    for (int nb = 2; nb <= num; nb++) {
        for (int sl = 1; sl <= num; sl++) {
            BI val; bi_zero(&val);
            for (int n = 1; n <= sl && n <= nb; n++) {
                int rem = nb - n;
                int nsl = (rem < n) ? rem : n;
                if (n == nb) {
                    /* partition [n] itself */
                    bi_inc(&val);
                } else {
                    bi_add_inplace(&val, dp_get(rem, nsl));
                }
            }
            *dp_get(nb, sl) = val;
        }
    }

    /* answer = dp[num][num] - 1 */
    BI ans = *dp_get(num, num);
    bi_dec(&ans);

    char *buf = malloc(NLIMBS * 10 + 2);
    if (!buf) { free(g_dp); return NULL; }
    int pos = sprintf(buf, "%lld", ans.limbs[ans.n-1]);
    for (int i = ans.n-2; i >= 0; i--) pos += sprintf(buf+pos, "%09lld", ans.limbs[i]);

    free(g_dp);
    g_dp = NULL;
    return buf;
}