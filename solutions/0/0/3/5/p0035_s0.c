/* Solution to Euler Problem 35: Circular Primes. */
#include "runner.h"

/* Sieve of Eratosthenes: mark composites in [0, max_num]; sieve[i] = 1 means composite. */
static void primes_sieve(int max_num, char *sieve) {
    /* sieve[i] = 1 means composite, 0 means prime */
    if (max_num < 2) return;
    sieve[0] = 1;
    sieve[1] = 1;
    for (int i = 2; (long long)i * i <= max_num; i++) {
        if (!sieve[i]) {
            for (int j = i * i; j <= max_num; j += i) {
                sieve[j] = 1;
            }
        }
    }
}

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
        /* rotation: str_num[i:] + str_num[:i] */
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

/* Count circular primes below max_limit. A multi-digit circular prime uses only digits {1,3,7,9},
   so the digit filter discards almost all primes before any rotation lookup. A hand-rolled
   Eratosthenes sieve gives O(1) primality; total O(n log log n) dominated by sieve construction. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int max_limit = parse_int(argv[1]);

    char *sieve = calloc((size_t)(max_limit + 1), 1);
    if (!sieve) {
        fprintf(stderr, "out of memory\n");
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }
    primes_sieve(max_limit, sieve);

    int count = 0;
    int rotations[12];

    for (int prime = 2; prime <= max_limit; prime++) {
        if (sieve[prime]) continue; /* not prime */

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
            if (rot > max_limit || sieve[rot]) {
                all_prime = 0;
                break;
            }
        }
        if (all_prime) count++;
    }

    free(sieve);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(count)); return _answer; }
}