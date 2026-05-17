/* Solution to Euler Problem 31: Coin Sums. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

/* Print a __int128 value to a buffer, return pointer to buffer */
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
 * argv[1..n-1] = coins as space-separated tokens from "[1, 2, 5, 10, 20, 50, 100, 200]"
 * argv[n]      = target_amount (last argument)
 */
static char result_str[128];

char *solve(int argc, char *argv[]) {
    if (argc < 3) { strcpy(result_str, "-1"); return result_str; }

    int target_amount = atoi(argv[argc - 1]);

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
    dp[0] = 1;

    /* Bottom-up coin-change DP: coin outer, amount inner */
    for (int ci = 0; ci < num_coins; ci++) {
        int coin = coins[ci];
        for (int i = coin; i <= target_amount; i++) {
            dp[i] += dp[i - coin];
        }
    }

    __int128 ans = dp[target_amount];
    free(dp);

    int128_to_str(ans, result_str, (int)sizeof(result_str));
    return result_str;
}

/* Usage: ./file <coins_list> <target_amount> [--runs=1] [--show]
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
        result = cur;
    }

    free(solve_argv);
    printf("%d %.17g %s\n", runs, total / (double)runs, result ? result : "-1");
    return rc;
}