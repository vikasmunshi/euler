/* Solution to Euler Problem 19: Counting Sundays. */
#include "runner.h"

/* Gregorian leap-year rule: divisible by 4, but century years only if divisible by 400. */
static int is_leap_year(int year) {
    return (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);
}

/* Days in a given month (1-based), with the leap-year correction for February. */
static int days_in_month(int year, int month) {
    int days[] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    if (month == 2 && is_leap_year(year)) return 29;
    return days[month - 1];
}

const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int end_year   = parse_int(argv[1]);
    int start_year = parse_int(argv[2]);

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

    { snprintf(_answer, sizeof _answer, "%lld", (long long)(count)); return _answer; }
}
