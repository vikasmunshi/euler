/* Solution to Euler Problem 23: Non-Abundant Sums. */
#include "runner.h"

/* Sum of the proper divisors of n, by trial division up to sqrt(n). */
static long long sum_proper_divisors(int n) {
    if (n <= 1) return 0;
    long long result = 1;
    for (int i = 2; (long long)i * i <= n; i++) {
        if (n % i == 0) {
            result += i;
            if (i != n / i) {
                result += n / i;
            }
        }
    }
    return result;
}

/* Classify abundant numbers via trial-division divisor sums, mark every pairwise sum of two,
   then sum the unmarked integers up to the fixed bound 28123 (above which every integer is an
   abundant sum). O(n*sqrt(n)) to classify, O(a^2) marking. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    (void)argc; (void)argv;
    int limit = 28123;

    /* Collect abundant numbers using trial division */
    int *abundant = malloc((size_t)(limit + 1) * sizeof(int));
    if (!abundant) { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    int abundant_count = 0;

    for (int i = 12; i <= limit; i++) {
        if (sum_proper_divisors(i) > i) {
            abundant[abundant_count++] = i;
        }
    }

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
