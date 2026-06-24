/* Solution to Euler Problem 52: Permuted Multiples. */
#include "runner.h"

static int cmp_char(const void *a, const void *b) {
    return (*(const char *)a) - (*(const char *)b);
}

/* Build the sorted-digit fingerprint of n: identical for any digit-permutation of n. */
static void sorted_digits(long long n, char *buf) {
    char tmp[32];
    int len = 0;
    if (n == 0) {
        buf[0] = '0';
        buf[1] = '\0';
        return;
    }
    /* Extract digits arithmetically (least-significant first); order is irrelevant before sorting. */
    while (n > 0) {
        tmp[len++] = (char)('0' + (n % 10));
        n /= 10;
    }
    qsort(tmp, (size_t)len, 1, cmp_char);
    memcpy(buf, tmp, (size_t)len);
    buf[len] = '\0';
}

/* Linear scan from x=1: x is the answer when 2x..Mx all share x's sorted-digit fingerprint.
   The digit-count constraint confines x to the low sixth of each band, so the scan is short.
   O(N * M * D): N the answer, M multiples (<=6), D digits (<=7). */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int multiples = 6;
    if (argc >= 2) {
        multiples = parse_int(argv[1]);
    }
    if (multiples < 2 || multiples > 6) {
        fprintf(stderr, "multiples must be between 2 and 6 inclusive.\n");
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }

    char fingerprint[32];
    char candidate[32];

    for (long long i = 1; ; i++) {
        sorted_digits(i, fingerprint);

        /* Early exit: most candidates mismatch at m=2, so the inner loop usually does one compare. */
        int all_match = 1;
        for (int m = 2; m <= multiples; m++) {
            sorted_digits(i * (long long)m, candidate);
            if (strcmp(fingerprint, candidate) != 0) {
                all_match = 0;
                break;
            }
        }

        if (all_match) {
            { snprintf(_answer, sizeof _answer, "%lld", (long long)(i)); return _answer; }
        }
    }
}