/* Solution to Euler Problem 78: Coin Partitions. */
#include "runner.h"

/*
 * Bottom-up DP for the partition function p(n) via Euler's pentagonal number
 * theorem: p(n) = sum_{k != 0} (-1)^(k+1) p(n - g(k)), where g(k) = k(3k-1)/2
 * are the generalized pentagonal numbers. Only O(sqrt(n)) terms per n have a
 * non-negative argument, so building the table to the answer N is O(N*sqrt(N)).
 * Since we only need divisibility, every value is reduced mod divisor, keeping
 * all stored numbers bounded. The first n with p(n) == 0 (mod divisor) is the
 * answer.
 */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int divisor = parse_int(argv[1]);

    /* Allocate a growing array for partition values mod divisor */
    int capacity = 100000;
    long long *partitions = malloc((size_t)capacity * sizeof(long long));
    if (!partitions) {
        fprintf(stderr, "Out of memory\n");
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }
    partitions[0] = 1;  /* p(0) = 1 seeds the recurrence */

    int n = 1;
    while (1) {
        if (n >= capacity) {
            /* Doubling growth keeps reallocs at O(log N) for unknown answer size */
            capacity *= 2;
            long long *tmp = realloc(partitions, (size_t)capacity * sizeof(long long));
            if (!tmp) {
                fprintf(stderr, "Out of memory\n");
                free(partitions);
                { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
            }
            partitions = tmp;
        }

        long long pval = 0;
        int k = 1;
        while (1) {
            /* Process the (k, -k) pentagonal pair together; one sign covers both */
            long long pent_pos = (long long)k * (3 * k - 1) / 2;
            long long pent_neg = (long long)k * (3 * k + 1) / 2;

            /* pent_pos is the smaller member, so this is the loop's termination test */
            if (pent_pos > n) break;

            int sign = (k % 2 == 1) ? 1 : -1;

            pval += sign * partitions[n - pent_pos];

            /* pent_neg can exceed n while pent_pos does not, so guard it separately */
            if (pent_neg <= n) {
                pval += sign * partitions[n - pent_neg];
            }

            k++;
        }

        /* Subtractions may leave pval negative, so normalize into [0, divisor) */
        pval = ((pval % divisor) + divisor) % divisor;
        partitions[n] = pval;

        if (pval == 0) {
            free(partitions);
            { snprintf(_answer, sizeof _answer, "%lld", (long long)((long long)n)); return _answer; }
        }

        n++;
    }
}