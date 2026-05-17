/* Solution to Euler Problem 40: Champernowne's Constant. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <math.h>

static int get_nth_digit_champernowne(long long n) {
    long long length_till_num_digits = 0;
    long long length_with_num_digits = 0;
    int num_digits = 0;

    while (length_with_num_digits < n) {
        num_digits++;
        length_till_num_digits = length_with_num_digits;
        /* num_digits * 9 * 10^(num_digits-1) */
        long long band = (long long)num_digits * 9;
        for (int k = 0; k < num_digits - 1; k++) band *= 10;
        length_with_num_digits += band;
    }

    long long offset_of_number = n - length_till_num_digits - 1;
    long long digit_in_number = offset_of_number % num_digits;
    long long number = 1;
    for (int k = 0; k < num_digits - 1; k++) number *= 10;
    number += offset_of_number / num_digits;

    /* Extract the digit_in_number-th digit from number */
    char buf[32];
    snprintf(buf, sizeof(buf), "%lld", number);
    return buf[digit_in_number] - '0';
}

long long solve(int argc, char *argv[]) {
    int i = atoi(argv[1]);

    long long product = 1;
    long long pos = 1;
    for (int k = 0; k <= i; k++) {
        int d = get_nth_digit_champernowne(pos);
        product *= d;
        pos *= 10;
    }
    return product;
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