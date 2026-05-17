/* Solution to Euler Problem 3: Largest Prime Factor. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <time.h>

static long long reduce(long long num, long long divisor) {
    num /= divisor;
    while (num % divisor == 0)
        num /= divisor;
    return num;
}

long long solve(int argc, char *argv[]) {
    long long number = atoll(argv[1]);
    long long remaining_number;
    long long largest_factor;

    if (number % 2 == 0) {
        remaining_number = reduce(number, 2);
        largest_factor = 2;
    } else {
        remaining_number = number;
        largest_factor = 1;
    }

    long long current_factor = 3;
    long long search_limit = (long long)sqrt((double)remaining_number);

    while (remaining_number > 1 && current_factor <= search_limit) {
        if (remaining_number % current_factor == 0) {
            remaining_number = reduce(remaining_number, current_factor);
            largest_factor = current_factor;
            search_limit = (long long)sqrt((double)remaining_number);
        }
        current_factor += 2;
    }

    return (remaining_number > 1) ? remaining_number : largest_factor;
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