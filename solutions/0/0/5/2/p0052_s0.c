/* Solution to Euler Problem 52: Permuted Multiples. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static int cmp_char(const void *a, const void *b) {
    return (*(const char *)a) - (*(const char *)b);
}

static void sorted_digits(long long n, char *buf) {
    /* Write sorted decimal digits of n into buf (null-terminated). */
    char tmp[32];
    int len = 0;
    if (n == 0) {
        buf[0] = '0';
        buf[1] = '\0';
        return;
    }
    while (n > 0) {
        tmp[len++] = (char)('0' + (n % 10));
        n /= 10;
    }
    qsort(tmp, (size_t)len, 1, cmp_char);
    memcpy(buf, tmp, (size_t)len);
    buf[len] = '\0';
}

long long solve(int argc, char *argv[]) {
    int multiples = 6;
    if (argc >= 2) {
        multiples = atoi(argv[1]);
    }
    if (multiples < 2 || multiples > 6) {
        fprintf(stderr, "multiples must be between 2 and 6 inclusive.\n");
        return -1;
    }

    char fingerprint[32];
    char candidate[32];

    for (long long i = 1; ; i++) {
        /* Compute sorted-digit fingerprint of i */
        sorted_digits(i, fingerprint);

        int all_match = 1;
        for (int m = 2; m <= multiples; m++) {
            sorted_digits(i * (long long)m, candidate);
            if (strcmp(fingerprint, candidate) != 0) {
                all_match = 0;
                break;
            }
        }

        if (all_match) {
            return i;
        }
    }
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