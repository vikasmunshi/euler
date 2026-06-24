/* Solution to Euler Problem 35: Circular Primes. */
#include "runner.h"
#include <primesieve.h>

/* Fill rotations[] with the cyclic digit rotations of num; return how many were produced. */
static int get_rotated_numbers(int num, int *rotations) {
    char str_num[12];
    snprintf(str_num, sizeof(str_num), "%d", num);
    int len = (int)strlen(str_num);
    int count = 0;
    if (len == 1) {
        rotations[count++] = num;
        return count;
    }
    char buf[12];
    for (int i = 1; i <= len; i++) {
        int pos = 0;
        for (int j = i; j < len; j++) buf[pos++] = str_num[j];
        for (int j = 0; j < i; j++) buf[pos++] = str_num[j];
        buf[pos] = '\0';
        rotations[count++] = atoi(buf);
    }
    return count;
}

/* True if num contains a digit that forces an even or multiple-of-5 rotation (0,2,4,5,6,8). */
static int has_bad_digit(int num) {
    char str_num[12];
    snprintf(str_num, sizeof(str_num), "%d", num);
    for (int i = 0; str_num[i]; i++) {
        char c = str_num[i];
        if (c == '0' || c == '2' || c == '4' || c == '5' || c == '6' || c == '8')
            return 1;
    }
    return 0;
}

/* Count circular primes below max_limit. Same digit-filter and rotation logic as s0, but prime
   generation is delegated to the tuned primesieve library; an indexed flag array gives O(1)
   primality. Runtime is dominated by sieve generation. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int max_limit = parse_int(argv[1]);

    /* Always allocate at least up to 10^6, mirroring the floor in s1.py */
    int sieve_limit = max_limit > 1000000 ? max_limit : 1000000;

    /* sieve[i] = 1 means prime (inverted polarity relative to s0) */
    char *sieve = calloc((size_t)(sieve_limit + 1), 1);
    if (!sieve) {
        fprintf(stderr, "out of memory\n");
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }

    size_t size = 0;
    int *primes = (int *)primesieve_generate_primes(0, (uint64_t)sieve_limit,
                                                     &size, INT_PRIMES);
    if (!primes) {
        free(sieve);
        fprintf(stderr, "out of memory\n");
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }
    for (size_t i = 0; i < size; i++) {
        sieve[primes[i]] = 1;
    }

    int count = 0;
    int rotations[12];

    for (size_t i = 0; i < size; i++) {
        int prime = primes[i];
        if (prime > max_limit) break;

        if (prime < 10) {
            count++;
            continue;
        }

        if (has_bad_digit(prime)) continue;

        int num_rot = get_rotated_numbers(prime, rotations);
        int all_prime = 1;
        for (int r = 0; r < num_rot; r++) {
            int rot = rotations[r];
            /* A rotation can exceed max_limit (and the sieve); treat any such value as composite. */
            if (rot > max_limit || !sieve[rot]) {
                all_prime = 0;
                break;
            }
        }
        if (all_prime) count++;
    }

    primesieve_free(primes);
    free(sieve);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(count)); return _answer; }
}