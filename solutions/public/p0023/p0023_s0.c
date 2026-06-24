/* Solution to Euler Problem 23: Non-Abundant Sums. */
#include "runner.h"

/* Sieve proper-divisor sums to flag abundant numbers, mark every pairwise sum of two
   abundant numbers, then sum the unmarked integers. Every integer above the fixed bound
   28123 is an abundant sum, so the search is finite. O(n log n) sieve, O(a^2) marking. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    (void)argc; (void)argv;
    int limit = 28123;

    /* Build aliquot sums using sieve approach */
    long long *div_sums = calloc((size_t)(limit + 1), sizeof(long long));
    if (!div_sums) { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }

    for (int i = 1; i <= limit / 2; i++) {
        for (int j = 2 * i; j <= limit; j += i) {
            div_sums[j] += i;
        }
    }

    /* Collect abundant numbers */
    int *abundant = malloc((size_t)(limit + 1) * sizeof(int));
    if (!abundant) { free(div_sums); { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; } }
    int abundant_count = 0;

    for (int i = 1; i <= limit; i++) {
        if (div_sums[i] > i) {
            abundant[abundant_count++] = i;
        }
    }
    free(div_sums);

    /* Mark all sums of two abundant numbers */
    char *is_abundant_sum = calloc((size_t)(limit + 1), sizeof(char));
    if (!is_abundant_sum) { free(abundant); { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; } }

    for (int i = 0; i < abundant_count; i++) {
        for (int j = i; j < abundant_count; j++) {
            int s = abundant[i] + abundant[j];
            if (s > limit) break;
            is_abundant_sum[s] = 1;
        }
    }
    free(abundant);

    /* Sum all numbers that cannot be written as sum of two abundant numbers */
    long long result = 0;
    for (int i = 1; i <= limit; i++) {
        if (!is_abundant_sum[i]) {
            result += i;
        }
    }
    free(is_abundant_sum);

    { snprintf(_answer, sizeof _answer, "%lld", (long long)(result)); return _answer; }
}
