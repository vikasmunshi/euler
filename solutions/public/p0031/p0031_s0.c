/* Solution to Euler Problem 31: Coin Sums. */
#include "runner.h"

/* Render a __int128 as a decimal string into buf via repeated division by 10. */
static char *int128_to_str(__int128 val, char *buf, int bufsize) {
    if (val == 0) {
        buf[0] = '0';
        buf[1] = '\0';
        return buf;
    }
    int neg = 0;
    if (val < 0) { neg = 1; val = -val; }
    char tmp[64];
    int idx = 0;
    while (val > 0) {
        tmp[idx++] = '0' + (int)(val % 10);
        val /= 10;
    }
    int out = 0;
    if (neg) buf[out++] = '-';
    for (int i = idx - 1; i >= 0 && out < bufsize - 1; i--) {
        buf[out++] = tmp[i];
    }
    buf[out] = '\0';
    return buf;
}

/*
 * Unbounded-knapsack coin-change count, mirroring the Python sibling; O(num_coins * target_amount)
 * time and O(target_amount) space. dp[i] is the number of unordered ways to make amount i with the
 * coins processed so far; iterating coins in the outer loop and amounts inner counts combinations,
 * not permutations. dp cells are __int128 because the target=100000 answer (23 digits) overflows
 * 64 bits.
 *
 * argv[1..n-1] = coins as space-separated tokens from "[1, 2, 5, 10, 20, 50, 100, 200]"
 * argv[n]      = target_amount (last argument)
 */
static char result_str[128];

const char *solve(int argc, char *argv[]) {
    if (argc < 3) { strcpy(result_str, "-1"); return result_str; }

    int target_amount = parse_int(argv[argc - 1]);

    /* Parse all coins from argv[1] .. argv[argc-2] */
    int coins[64];
    int num_coins = 0;

    for (int i = 1; i <= argc - 2; i++) {
        char *p = argv[i];
        while (*p) {
            if (*p >= '0' && *p <= '9') {
                coins[num_coins++] = (int)strtol(p, &p, 10);
            } else {
                p++;
            }
        }
    }

    if (num_coins == 0 || target_amount < 0) {
        strcpy(result_str, "-1");
        return result_str;
    }

    /* Allocate DP table using __int128 */
    __int128 *dp = (__int128 *)calloc((size_t)(target_amount + 1), sizeof(__int128));
    if (!dp) { strcpy(result_str, "-1"); return result_str; }
    dp[0] = 1;  /* one way to make zero: take no coins */

    /* Bottom-up coin-change DP: coin outer, amount inner (counts combinations). */
    for (int ci = 0; ci < num_coins; ci++) {
        int coin = coins[ci];
        /* Upward sweep reuses dp[i - coin] within this pass, making the coin unbounded. */
        for (int i = coin; i <= target_amount; i++) {
            dp[i] += dp[i - coin];
        }
    }

    __int128 ans = dp[target_amount];
    free(dp);

    int128_to_str(ans, result_str, (int)sizeof(result_str));
    return result_str;
}