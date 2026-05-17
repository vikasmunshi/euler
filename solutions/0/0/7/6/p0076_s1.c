/* Solution to Euler Problem 76: Counting Summations. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

/* Big integer using base 10^9 limbs, little-endian */
#define BASE 1000000000LL
#define MAX_LIMBS 16

typedef struct {
    long long limbs[MAX_LIMBS];
    int n;
} BigInt;

static void bigint_set(BigInt *a, long long val) {
    memset(a->limbs, 0, sizeof(a->limbs));
    a->n = 1;
    a->limbs[0] = 0;
    if (val == 0) return;
    a->n = 0;
    while (val > 0) {
        a->limbs[a->n++] = val % BASE;
        val /= BASE;
    }
}

static void bigint_add_inplace(BigInt *a, const BigInt *b) {
    long long carry = 0;
    int maxn = (a->n > b->n) ? a->n : b->n;
    for (int i = 0; i < maxn || carry; i++) {
        long long sum = carry;
        if (i < a->n) sum += a->limbs[i];
        else a->limbs[i] = 0;
        if (i < b->n) sum += b->limbs[i];
        a->limbs[i] = sum % BASE;
        carry = sum / BASE;
        if (i >= a->n) a->n = i + 1;
    }
    if (a->n < maxn) a->n = maxn;
}

static void bigint_print_to_buf(const BigInt *a, char *buf) {
    int pos = 0;
    pos += sprintf(buf + pos, "%lld", a->limbs[a->n - 1]);
    for (int i = a->n - 2; i >= 0; i--) {
        pos += sprintf(buf + pos, "%09lld", a->limbs[i]);
    }
}

static char *solve(int argc, char *argv[]) {
    int num = (argc > 1) ? atoi(argv[1]) : 100;

    if (num <= 0) {
        char *buf = malloc(4);
        strcpy(buf, "0");
        return buf;
    }

    /*
     * Bottom-up DP: dp[nb][sl] = num_partitions(number=nb, slots=sl)
     * Python base: number<=1 -> return number
     * We need a 2D table of BigInt. For num=1000, that's 1001*1001 = ~1M BigInts.
     * Each BigInt is MAX_LIMBS*8 + 4 bytes = 132 bytes -> ~132MB. Too much.
     *
     * Optimization: note that dp[nb][sl] only depends on dp[nb-n][...] for n=1..sl,
     * i.e., rows with smaller nb. We process nb in order. But we need all previous rows.
     *
     * Alternative: observe that num_partitions(number, slots) is equivalent to the
     * standard partition DP: number of ways to partition `number` using parts 1..slots.
     * This equals the coin-change count with coins 1..slots.
     *
     * Standard coin DP: dp2[j] = number of ways to make j using coins processed so far.
     * For each coin value c from 1 to num: dp2[j] += dp2[j-c] for j=c..num.
     * This gives p(n) in the dp2[num] slot.
     *
     * But this is a different algorithm (s0-style). We must faithfully translate s1.
     *
     * For s1, let's use a 1D optimization:
     * dp[nb][sl] = dp[nb][sl-1] + dp[nb-sl][min(nb-sl, sl)]
     * (adding one more allowed part size sl)
     * with dp[nb][0] = 0, dp[0][sl] = 0 (adjusted: dp[0][0]=1 base).
     *
     * Actually let's think differently. The Python recursion:
     * count(nb, sl) = sum_{n=1}^{sl} count(nb-n, min(nb-n, n)) + (1 if nb<=sl else 0)
     *
     * Note: count(nb, min(nb-n, n)) where min(nb-n,n):
     *   if n <= nb-n, i.e. n <= nb/2: min = n, so count(nb-n, n)
     *   if n > nb/2: min = nb-n, so count(nb-n, nb-n) = p(nb-n) in full
     *
     * This has O(n^2) states but computing each takes O(n) work = O(n^3) total.
     * For n=1000, that's 10^9 BigInt ops - too slow.
     *
     * Use the standard partition recurrence instead, which is what s1 computes:
     * Actually num_partitions(number, slots) with the given recursion IS p(number)
     * when slots=number. The 2D table approach is needed for correctness.
     *
     * For memory, use a simpler approach: store only necessary rows.
     * dp[nb][sl] = dp[nb][sl-1] + dp[nb-sl][min(nb-sl,sl)]
     * We iterate sl from 1 to num for each nb. This allows column-by-column computation
     * but we still need all (nb, sl) pairs.
     *
     * For n=1000, allocate a flat array of BigInt but use a more compact representation.
     * Actually for n=100 (main test), 101*101 = ~10K BigInts, easily fits.
     * For n=1000, 1001*1001 ~= 1M BigInts * 132 bytes = 132MB. Borderline.
     * Let's reduce MAX_LIMBS to fit the actual values:
     * p(1000) ~ 2.4e31 which needs about 4 limbs (base 10^9). Use 8 limbs to be safe.
     */

    /* Use recurrence: dp[nb][sl] = dp[nb][sl-1] + dp[nb-sl][min(nb-sl,sl)]
     * with dp[nb][0] = 0 for nb>0, dp[0][sl] = 1 for sl>=0 (empty partition).
     * And handle Python base case: number<=1 -> return number.
     * When nb=1: dp[1][sl] = 1 for sl>=1 (one partition: [1]).
     * When nb=0: not reached in the sum (we start from n=1).
     * The "+1 if nb<=sl" in Python accounts for the whole-number partition.
     * dp[nb][nb] = p(nb), then answer = dp[num][num] - 1.
     */

    /* Flatten to 1D: index = nb*(num+1)+sl */
    size_t sz = (size_t)(num + 1) * (size_t)(num + 1);

    /* Use smaller BigInt for memory: 8 limbs supports up to ~7e71 */
#define NLIMBS 8
    typedef struct { long long limbs[NLIMBS]; int n; } BI;

    BI *dp = calloc(sz, sizeof(BI));
    if (!dp) { fprintf(stderr, "out of memory\n"); return NULL; }

#define DP(nb,sl) dp[(nb)*(num+1)+(sl)]
#define BI_ZERO(x) do { memset((x).limbs,0,sizeof((x).limbs)); (x).n=1; } while(0)
#define BI_ONE(x)  do { memset((x).limbs,0,sizeof((x).limbs)); (x).limbs[0]=1; (x).n=1; } while(0)

    /* Initialize: dp[nb][sl=0] = 0 (already zero from calloc, set n=1) */
    for (int nb = 0; nb <= num; nb++) {
        for (int sl = 0; sl <= num; sl++) {
            DP(nb,sl).n = 1; /* zero */
        }
    }

    /* dp[0][sl] conceptually = 1 (empty partition), but Python base says number<=1 -> number.
     * So dp[0][sl]=0, dp[1][sl]=1 for sl>=1. The "+1 if nb<=sl" adds the whole-number partition.
     * Let's just directly implement the Python recursion bottom-up.
     * count(nb, sl) = sum_{n=1}^{min(sl,nb)} count(nb-n, min(nb-n,n)) + (1 if nb<=sl else 0)
     * Fill nb from 2 upward (nb=0 -> 0, nb=1 -> 1).
     */
    for (int sl = 1; sl <= num; sl++) {
        DP(1,sl).limbs[0] = 1; DP(1,sl).n = 1;
    }

    for (int nb = 2; nb <= num; nb++) {
        for (int sl = 1; sl <= num; sl++) {
            BI val; BI_ZERO(val);
            for (int n = 1; n <= sl && n <= nb; n++) {
                int rem = nb - n;
                int nsl = (rem < n) ? rem : n;
                /* add DP(rem, nsl) to val */
                BI *src = &DP(rem, nsl);
                long long carry = 0;
                int maxn = (val.n > src->n) ? val.n : src->n;
                for (int i = 0; i < maxn || carry; i++) {
                    long long sum = carry;
                    if (i < val.n) sum += val.limbs[i];
                    else val.limbs[i] = 0;
                    if (i < src->n) sum += src->limbs[i];
                    val.limbs[i] = sum % BASE;
                    carry = sum / BASE;
                    if (i >= val.n) val.n = i + 1;
                }
                if (val.n < maxn) val.n = maxn;
            }
            if (nb <= sl) val.limbs[0]++; /* +1 for whole-number partition, no carry needed for small +1? */
            /* Handle carry for +1 */
            for (int i = 0; val.limbs[i] >= BASE; i++) {
                val.limbs[i+1] += val.limbs[i] / BASE;
                val.limbs[i] %= BASE;
                if (i+1 >= val.n) val.n = i+2;
            }
            DP(nb, sl) = val;
        }
    }

    /* answer = dp[num][num] - 1 */
    BI ans = DP(num, num);
    ans.limbs[0]--;
    if (ans.limbs[0] < 0) {
        /* borrow */
        int i = 0;
        while (ans.limbs[i] < 0) {
            ans.limbs[i] += BASE;
            ans.limbs[i+1]--;
            i++;
        }
        while (ans.n > 1 && ans.limbs[ans.n-1] == 0) ans.n--;
    }

    char *buf = malloc(NLIMBS * 10 + 2);
    if (!buf) { free(dp); return NULL; }
    int pos = sprintf(buf, "%lld", ans.limbs[ans.n-1]);
    for (int i = ans.n-2; i >= 0; i--) pos += sprintf(buf+pos, "%09lld", ans.limbs[i]);

    free(dp);
#undef DP
#undef BI_ZERO
#undef BI_ONE
#undef NLIMBS
    return buf;
}

/* Usage: ./file <kwarg>... [--runs=1] [--show]
 * Output: "<runs> <avg_seconds> <result>" */
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
            if (cur && strcmp(cur, result) != 0) {
                fprintf(stderr, "Inconsistent results: %s vs %s\n", cur, result);
                rc = 1;
            }
            free(result);
        }
        result = cur;
    }

    free(solve_argv);
    printf("%d %.17g %s\n", runs, total / (double)runs, result ? result : "NULL");
    free(result);
    return rc;
}