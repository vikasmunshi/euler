/* Solution to Euler Problem 92: Square Digit Chains. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static int terminates_in_89(int n) {
    while (n != 1 && n != 89) {
        int next = 0;
        while (n) {
            int d = n % 10;
            next += d * d;
            n /= 10;
        }
        n = next;
    }
    return n == 89;
}

long long solve(int argc, char *argv[]) {
    int power_of_10 = atoi(argv[1]);

    /* sq = squares of digits 1..9 */
    int sq[9] = {1, 4, 9, 16, 25, 36, 49, 64, 81};

    /* Maximum size of a after power_of_10 iterations: 1 + power_of_10 * 81 */
    int max_size = 1 + power_of_10 * 81;

    long long *a = calloc((size_t)max_size, sizeof(long long));
    int *is89 = calloc((size_t)max_size, sizeof(int));
    if (!a || !is89) {
        fprintf(stderr, "out of memory\n");
        free(a); free(is89);
        return -1;
    }

    /* Initialize: a = [1], is89 = [0] (index 0: terminates_in_89(0) is false) */
    a[0] = 1;
    int cur_len = 1;
    is89[0] = 0; /* 0 doesn't terminate in 89 (it's not a valid starting point but doesn't matter) */

    long long result = 0;

    for (int n = 1; n <= power_of_10; n++) {
        int prev_len = cur_len;
        int new_len = prev_len + 81;

        /* b = a[0..prev_len-1], extend a to new_len */
        /* Save previous values */
        long long *b = malloc((size_t)prev_len * sizeof(long long));
        if (!b) {
            fprintf(stderr, "out of memory\n");
            free(a); free(is89);
            return -1;
        }
        memcpy(b, a, (size_t)prev_len * sizeof(long long));

        /* Zero out the extension */
        memset(a + prev_len, 0, 81 * sizeof(long long));

        /* Extend is89 for indices prev_len..new_len-1 */
        for (int i = prev_len; i < new_len; i++) {
            is89[i] = terminates_in_89(i);
        }

        /* Convolve: for each i in b, for each digit square s, a[i+s] += b[i] */
        for (int i = 0; i < prev_len; i++) {
            if (b[i] == 0) continue;
            for (int j = 0; j < 9; j++) {
                a[i + sq[j]] += b[i];
            }
        }

        cur_len = new_len;
        free(b);

        /* Sum a[i] for i where is89[i] */
        if (n == power_of_10) {
            result = 0;
            for (int i = 0; i < cur_len; i++) {
                if (is89[i]) {
                    result += a[i];
                }
            }
        }
    }

    free(a);
    free(is89);
    return result;
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