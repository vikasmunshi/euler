/* Solution to Euler Problem 24: Lexicographic Permutations. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static long long factorial(int n) {
    long long result = 1;
    for (int i = 2; i <= n; i++) {
        result *= i;
    }
    return result;
}

/* Recursive function: digits is a null-terminated string of available digits,
   permutation_number is 1-based. Returns a heap-allocated string. */
static char *recursive_solution(const char *digits, long long permutation_number) {
    int len = (int)strlen(digits);
    if (len == 1) {
        char *result = malloc(2);
        result[0] = digits[0];
        result[1] = '\0';
        return result;
    }

    long long fact = factorial(len - 1);
    long long current = (permutation_number - 1) / fact;
    long long remaining = (permutation_number - 1) % fact;

    /* Build new digits string with digits[current] removed */
    char *new_digits = malloc((size_t)len);
    int j = 0;
    for (int i = 0; i < len; i++) {
        if (i != (int)current) {
            new_digits[j++] = digits[i];
        }
    }
    new_digits[j] = '\0';

    char *sub = recursive_solution(new_digits, remaining + 1);
    free(new_digits);

    char *result = malloc((size_t)(len + 1));
    result[0] = digits[current];
    strcpy(result + 1, sub);
    free(sub);

    return result;
}

char *solve(int argc, char *argv[]) {
    const char *digits = argv[1];
    long long permutation_number = atoll(argv[2]);
    return recursive_solution(digits, permutation_number);
}

/* Usage: ./file <digits> <permutation_number> [--runs=1] [--show]
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
    int has_result = 0;

    for (int r = 0; r < runs; r++) {
        struct timespec t0, t1;
        clock_gettime(CLOCK_MONOTONIC, &t0);
        char *cur = solve(solve_argc, solve_argv);
        clock_gettime(CLOCK_MONOTONIC, &t1);
        total += (double)(t1.tv_sec - t0.tv_sec)
               + (double)(t1.tv_nsec - t0.tv_nsec) * 1e-9;
        if (has_result) {
            if (strcmp(cur, result) != 0) {
                fprintf(stderr, "Expected consistent result, got %s previous result=%s\n",
                        cur, result);
                rc = 1;
            }
            free(cur);
        } else {
            result = cur;
            has_result = 1;
        }
    }

    free(solve_argv);
    printf("%d %.17g %s\n", runs, total / (double)runs, result ? result : "");
    free(result);
    return rc;
}