/* Solution to Euler Problem 7: 10 001st Prime. */
#include "runner.h"
#include <math.h>

/* Sieve of Sundaram over [1, n*ln n] (the prime-number-theorem bound on the n-th prime):
   each surviving index k denotes the odd prime 2k+1, so the (n-2)-th survivor (after the
   special-cased prime 2) is the n-th prime. O(M log M) marking for M = n*ln n. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int n = parse_int(argv[1]);

    if (n == 1) { snprintf(_answer, sizeof _answer, "%lld", (long long)(2)); return _answer; }

    int max_expected_value = (int)(n * log((double)n));

    int *numbers = (int *)malloc((size_t)(max_expected_value + 1) * sizeof(int));
    if (!numbers) {
        fprintf(stderr, "Out of memory\n");
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }
    for (int k = 0; k <= max_expected_value; k++) {
        numbers[k] = k;
    }

    for (int i = 1; i <= max_expected_value; i++) {
        if (numbers[i] == 0) continue;
        for (int j = i; ; j++) {
            long long idx = (long long)i + j + 2LL * i * j;
            if (idx > max_expected_value) break;
            numbers[idx] = 0;
        }
    }

    /* Collect non-zero indices and pick (n-2)-th (0-indexed), then convert to odd number */
    /* We need the (n-2)-th surviving index (skipping index 0 which maps to odd 1) */
    /* numbers[0] = 0 already, so we count non-zero entries from index 1 onward */
    int count = 0;
    long long result = -1;
    for (int k = 1; k <= max_expected_value; k++) {
        if (numbers[k] != 0) {
            if (count == n - 2) {
                result = 2LL * k + 1;
                break;
            }
            count++;
        }
    }

    free(numbers);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(result)); return _answer; }
}
