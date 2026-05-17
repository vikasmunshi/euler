/* Solution to Euler Problem 4: Largest Palindrome Product. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static int is_palindromic(long long number) {
    char buf[32];
    snprintf(buf, sizeof(buf), "%lld", number);
    int len = (int)strlen(buf);
    for (int i = 0, j = len - 1; i < j; i++, j--) {
        if (buf[i] != buf[j]) return 0;
    }
    return 1;
}

long long solve(int argc, char *argv[], int show) {
    int n = atoi(argv[1]);

    long long max_number = 1;
    for (int i = 0; i < n; i++) max_number *= 10;
    max_number -= 1;

    long long min_number = 1;
    for (int i = 0; i < n - 1; i++) min_number *= 10;

    long long max_multiple_11 = max_number - max_number % 11;

    long long largest_palindrome = 0;
    long long a_max = 0, b_max = 0;

    for (long long a = max_number; a > min_number; a--) {
        int a_is_multiple_11 = (a % 11 == 0);
        long long b_start = a_is_multiple_11 ? max_number : max_multiple_11;
        long long b_step  = a_is_multiple_11 ? 1 : 11;

        for (long long b = b_start; b >= a; b -= b_step) {
            long long ab = a * b;
            if (ab <= largest_palindrome) break;
            if (is_palindromic(ab)) {
                a_max = a; b_max = b; largest_palindrome = ab;
                break;
            }
        }
    }

    if (show)
        printf("Largest palindrome that is a multiple of two %d-digit numbers is "
               "%lld (%lldx%lld)\n", n, largest_palindrome, a_max, b_max);

    return largest_palindrome;
}

/* Usage: ./file <kwarg>... [--runs=1] [--show]
 * Output: "<runs> <avg_seconds> <result>" */
int main(int argc, char *argv[]) {
    int runs = 1;
    int show = 0;

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
        if (strcmp(argv[i], "--show") == 0) { show = 1; continue; }
        solve_argv[solve_argc++] = argv[i];
    }

    long long result = 0;
    double total = 0.0;
    int rc = 0;
    int has_result = 0;

    for (int r = 0; r < runs; r++) {
        struct timespec t0, t1;
        clock_gettime(CLOCK_MONOTONIC, &t0);
        long long cur = solve(solve_argc, solve_argv, show);
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