/* Solution to Euler Problem 51: Prime Digit Replacements. */
#include "runner.h"

/* Sundaram sieve: returns array of primes up to max_num, sets *count. */
static int *sundaram_sieve(int max_num, int *count) {
    if (max_num < 2) {
        *count = 0;
        return NULL;
    }
    long long n = ((long long)max_num - 1) / 2;
    /* Byte-per-element marking array: simpler than a bit sieve, ample for these limits. */
    unsigned char *marked = calloc((size_t)(n + 1), 1);
    if (!marked) { *count = 0; return NULL; }

    /* Odd value 2k+1 is composite exactly when k = i + j + 2ij for 1 <= i <= j. */
    for (long long i = 1; i <= n; i++) {
        long long j = i;
        while (i + j + 2LL * i * j <= n) {
            marked[i + j + 2LL * i * j] = 1;
            j++;
        }
    }

    /* Count primes */
    long long cnt = (max_num >= 2) ? 1 : 0; /* for 2 */
    for (long long i = 1; i <= n; i++) {
        if (!marked[i]) cnt++;
    }

    int *primes = malloc((size_t)cnt * sizeof(int));
    if (!primes) { free(marked); *count = 0; return NULL; }

    /* Prepend 2 manually, then each unmarked index i yields the prime 2i+1. */
    int idx = 0;
    if (max_num >= 2) primes[idx++] = 2;
    for (long long i = 1; i <= n; i++) {
        if (!marked[i]) primes[idx++] = (int)(2 * i + 1);
    }

    free(marked);
    *count = (int)cnt;
    return primes;
}

/* Trial division up to sqrt(num); used per candidate, not as a second sieve. */
static int is_prime(int num) {
    if (num < 2) return 0;
    if (num == 2) return 1;
    if (num % 2 == 0) return 0;
    for (int i = 3; (long long)i * i <= num; i += 2) {
        if (num % i == 0) return 0;
    }
    return 1;
}

/* Scan primes ascending; for each, replace a single digit value (only digits 0..9-prime_run
   can start an eight-family) with values from that digit up to 9, counting forward-only members
   that stay prime. Return the first prime whose family reaches prime_run. O(P * D) over P primes
   below 10^num_digits with D-digit strings. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int num_digits = parse_int(argv[1]);
    int prime_run  = parse_int(argv[2]);

    /* Compute 10^num_digits */
    int limit = 1;
    for (int i = 0; i < num_digits; i++) limit *= 10;

    int prime_count = 0;
    int *primes = sundaram_sieve(limit, &prime_count);
    if (!primes) { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }

    long long answer = -1;

    for (int pi = 0; pi < prime_count && answer < 0; pi++) {
        int prime = primes[pi];

        /* Convert prime to string */
        char prime_str[32];
        snprintf(prime_str, sizeof(prime_str), "%d", prime);
        int plen = (int)strlen(prime_str);

        /* Iterate over replaced digits: "0123456789"[:10 - prime_run] */
        int max_replaced_digit = 10 - prime_run; /* exclusive upper bound */
        for (int rd = 0; rd < max_replaced_digit && answer < 0; rd++) {
            char replaced = (char)('0' + rd);

            /* Check if this digit appears in prime_str */
            int found = 0;
            for (int k = 0; k < plen; k++) {
                if (prime_str[k] == replaced) { found = 1; break; }
            }
            if (!found) continue;

            /* For each replacement digit >= replaced digit, substitute all occurrences,
               counting only same-length members that are >= prime and prime themselves;
               forward-only counting guarantees the first match is the smallest member. */
            int seq_count = 0;

            for (int rep = rd; rep <= 9; rep++) {
                char replacement = (char)('0' + rep);

                /* Build new number string */
                char new_str[32];
                int ni = 0;
                for (int k = 0; k < plen; k++) {
                    if (prime_str[k] == replaced)
                        new_str[ni++] = replacement;
                    else
                        new_str[ni++] = prime_str[k];
                }
                new_str[ni] = '\0';

                /* Skip leading zeros: result would be a shorter number, not a valid member. */
                if (new_str[0] == '0') continue;

                int new_val = atoi(new_str);

                if (new_val >= prime && is_prime(new_val)) {
                    seq_count++;
                }
            }

            if (seq_count == prime_run) {
                answer = (long long)prime;
            }
        }
    }

    free(primes);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(answer)); return _answer; }
}