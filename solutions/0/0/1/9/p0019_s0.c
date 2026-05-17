/* Solution to Euler Problem 19: Counting Sundays. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static int is_leap_year(int year) {
    return (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);
}

static int days_in_month(int year, int month) {
    int days[] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    if (month == 2 && is_leap_year(year)) return 29;
    return days[month - 1];
}

long long solve(int argc, char *argv[]) {
    int end_year   = atoi(argv[1]);
    int start_year = atoi(argv[2]);

    /* Count days from 1 Jan 1900 (Monday = 1) to 1 Jan start_year,
     * then iterate over each first-of-month in [start_year, end_year]
     * checking if it's a Sunday (day_of_week == 0, where Monday=1..Sunday=7).
     * We use 0-based: Monday=0, ..., Sunday=6. */

    /* Compute day of week for 1 Jan 1900: Monday = 0 */
    int dow = 0; /* Monday */

    /* Advance from 1 Jan 1900 to 1 Jan start_year */
    for (int y = 1900; y < start_year; y++) {
        dow = (dow + (is_leap_year(y) ? 366 : 365)) % 7;
    }

    long long count = 0;

    for (int y = start_year; y <= end_year; y++) {
        for (int m = 1; m <= 12; m++) {
            /* dow is the day of week for the 1st of this month/year */
            /* Sunday = 6 (Monday=0, Tuesday=1, ..., Sunday=6) */
            if (dow == 6) count++;
            /* Advance by days in this month */
            dow = (dow + days_in_month(y, m)) % 7;
        }
    }

    return count;
}

/* Usage: ./file <end_year> <start_year> [--runs=1] [--show]
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