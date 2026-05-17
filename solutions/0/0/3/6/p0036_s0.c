/* Solution to Euler Problem 36: Double-base Palindromes. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static int is_binary_palindrome(long long n) {
    /* Build binary representation and check if it's a palindrome */
    if (n <= 0) return 0;
    char bits[64];
    int len = 0;
    long long tmp = n;
    while (tmp > 0) {
        bits[len++] = (char)(tmp & 1);
        tmp >>= 1;
    }
    /* bits is stored LSB first, so check if it reads the same forwards and backwards */
    for (int i = 0; i < len / 2; i++) {
        if (bits[i] != bits[len - 1 - i]) return 0;
    }
    return 1;
}

static long long int_pow10(int exp) {
    long long result = 1;
    for (int i = 0; i < exp; i++) result *= 10;
    return result;
}

long long solve(int argc, char *argv[]) {
    int max_digits = atoi(argv[1]);
    long long total = 0;

    /* Single-digit palindromes: 1-9 */
    for (int digit = 1; digit <= 9; digit++) {
        if (is_binary_palindrome((long long)digit)) {
            total += digit;
        }
    }

    /* Multi-digit palindromes generated from left half */
    long long limit = int_pow10(max_digits / 2);
    for (long long digits = 1; digits < limit; digits++) {
        /* Convert digits to string */
        char digits_str[20];
        snprintf(digits_str, sizeof(digits_str), "%lld", digits);
        int num_digits = (int)strlen(digits_str);

        /* Build reversed string */
        char digits_rev[20];
        for (int i = 0; i < num_digits; i++) {
            digits_rev[i] = digits_str[num_digits - 1 - i];
        }
        digits_rev[num_digits] = '\0';

        /* Even-length palindrome: digits_str + digits_rev */
        char even_str[40];
        snprintf(even_str, sizeof(even_str), "%s%s", digits_str, digits_rev);
        long long even_num = atoll(even_str);
        if (is_binary_palindrome(even_num)) {
            total += even_num;
        }

        /* Odd-length palindromes: digits_str + mid_digit + digits_rev */
        if (2 * num_digits < max_digits) {
            for (int mid = 0; mid <= 9; mid++) {
                char odd_str[42];
                snprintf(odd_str, sizeof(odd_str), "%s%d%s", digits_str, mid, digits_rev);
                long long odd_num = atoll(odd_str);
                if (is_binary_palindrome(odd_num)) {
                    total += odd_num;
                }
            }
        }
    }

    return total;
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