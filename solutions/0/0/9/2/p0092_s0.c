/* Solution to Euler Problem 92: Square Digit Chains. */
#include "runner.h"

/* Return 1 if the square-digit-sum chain from n reaches the 89-cycle rather than 1. */
static int terminates_in_89(int n) {
    while (n != 1 && n != 89) {
        int next = 0;
        while (n) {
            int d = n % 10;
            next += d * d;
            n /= 10;
        }
        n = next;
    }
    return n == 89;
}

/* Count d-digit values reaching 89 by convolving the per-digit square distribution; O(d^2 * 81).
   The chain depends only on the digit-square-sum, so a[s] counts strings with sum s, grown one
   digit at a time, and only the <= 81*d distinct sums need classifying via terminates_in_89. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int power_of_10 = parse_int(argv[1]);

    /* sq = squares of digits 1..9 */
    int sq[9] = {1, 4, 9, 16, 25, 36, 49, 64, 81};

    /* Maximum size of a after power_of_10 iterations: 1 + power_of_10 * 81 */
    int max_size = 1 + power_of_10 * 81;

    /* long long counts since they exceed 32 bits once power_of_10 reaches 9. */
    long long *a = calloc((size_t)max_size, sizeof(long long));
    int *is89 = calloc((size_t)max_size, sizeof(int));
    if (!a || !is89) {
        fprintf(stderr, "out of memory\n");
        free(a); free(is89);
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }

    /* Initialize: a = [1], is89 = [0] (index 0: terminates_in_89(0) is false) */
    a[0] = 1;
    int cur_len = 1;
    is89[0] = 0; /* 0 doesn't terminate in 89 (it's not a valid starting point but doesn't matter) */

    long long result = 0;

    for (int n = 1; n <= power_of_10; n++) {
        int prev_len = cur_len;
        int new_len = prev_len + 81;

        /* b = a[0..prev_len-1], extend a to new_len */
        /* Save previous values */
        long long *b = malloc((size_t)prev_len * sizeof(long long));
        if (!b) {
            fprintf(stderr, "out of memory\n");
            free(a); free(is89);
            { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
        }
        memcpy(b, a, (size_t)prev_len * sizeof(long long));

        /* Zero out the extension */
        memset(a + prev_len, 0, 81 * sizeof(long long));

        /* Extend is89 for indices prev_len..new_len-1 */
        for (int i = prev_len; i < new_len; i++) {
            is89[i] = terminates_in_89(i);
        }

        /* Convolve: for each i in b, for each digit square s, a[i+s] += b[i] */
        for (int i = 0; i < prev_len; i++) {
            if (b[i] == 0) continue;
            for (int j = 0; j < 9; j++) {
                a[i + sq[j]] += b[i];
            }
        }

        cur_len = new_len;
        free(b);

        /* Sum a[i] for i where is89[i] */
        if (n == power_of_10) {
            result = 0;
            for (int i = 0; i < cur_len; i++) {
                if (is89[i]) {
                    result += a[i];
                }
            }
        }
    }

    free(a);
    free(is89);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(result)); return _answer; }
}