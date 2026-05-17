/* Solution to Euler Problem 29: Distinct Powers. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

/* Prime factorization: returns array of (prime, exponent) pairs.
   factors is filled with alternating prime, exponent values.
   Returns number of distinct prime factors. */
static int prime_factorization(int n, int *primes, int *exponents) {
    int count = 0;
    int d = 2;
    while (d * d <= n) {
        if (n % d == 0) {
            int exp = 0;
            while (n % d == 0) {
                n /= d;
                exp++;
            }
            primes[count] = d;
            exponents[count] = exp;
            count++;
        }
        d++;
    }
    if (n > 1) {
        primes[count] = n;
        exponents[count] = 1;
        count++;
    }
    return count;
}

/* Simple hash set for tuples of (prime, scaled_exponent) pairs.
   We encode each signature as a string key for hashing. */

#define HASH_SIZE (1 << 22)  /* 4M buckets */
#define HASH_MASK (HASH_SIZE - 1)

typedef struct HashNode {
    char *key;
    struct HashNode *next;
} HashNode;

static HashNode *hash_table[HASH_SIZE];
static int hash_count = 0;

static void hash_clear(void) {
    for (int i = 0; i < HASH_SIZE; i++) {
        HashNode *node = hash_table[i];
        while (node) {
            HashNode *next = node->next;
            free(node->key);
            free(node);
            node = next;
        }
        hash_table[i] = NULL;
    }
    hash_count = 0;
}

static unsigned int hash_str(const char *s) {
    unsigned int h = 5381;
    while (*s) {
        h = ((h << 5) + h) + (unsigned char)*s;
        s++;
    }
    return h & HASH_MASK;
}

/* Returns 1 if inserted (new), 0 if already existed */
static int hash_insert(const char *key) {
    unsigned int h = hash_str(key);
    HashNode *node = hash_table[h];
    while (node) {
        if (strcmp(node->key, key) == 0) return 0;
        node = node->next;
    }
    HashNode *new_node = malloc(sizeof(HashNode));
    new_node->key = strdup(key);
    new_node->next = hash_table[h];
    hash_table[h] = new_node;
    hash_count++;
    return 1;
}

/* Big integer power for small ranges: a^b stored as string via repeated multiplication.
   For the main/dev case (a<=100, b<=100), we use a big-integer approach.
   Max value: 100^100 has about 200 decimal digits. */

#define BIGNUM_DIGITS 220

static void bignum_mul(int *digits, int *ndigits, int factor) {
    long long carry = 0;
    for (int i = 0; i < *ndigits; i++) {
        long long val = (long long)digits[i] * factor + carry;
        digits[i] = (int)(val % 1000000000LL);
        carry = val / 1000000000LL;
    }
    while (carry > 0) {
        digits[(*ndigits)++] = (int)(carry % 1000000000LL);
        carry /= 1000000000LL;
    }
}

/* Convert big number to string key */
static void bignum_to_str(int *digits, int ndigits, char *buf) {
    int pos = 0;
    pos += sprintf(buf + pos, "%d", digits[ndigits - 1]);
    for (int i = ndigits - 2; i >= 0; i--) {
        pos += sprintf(buf + pos, "%09d", digits[i]);
    }
    buf[pos] = '\0';
}

long long solve(int argc, char *argv[]) {
    int a_min = atoi(argv[1]);
    int a_max = atoi(argv[2]);
    int b_min = atoi(argv[3]);
    int b_max = atoi(argv[4]);

    memset(hash_table, 0, sizeof(hash_table));
    hash_count = 0;

    int threshold = (a_max < b_max) ? a_max : b_max;

    if (threshold <= 100) {
        /* Direct big-integer computation */
        /* We'll compute a^b_min first, then multiply by a for each subsequent b */
        int digits[BIGNUM_DIGITS];
        char buf[BIGNUM_DIGITS * 10 + 10];

        for (int a = a_min; a <= a_max; a++) {
            /* Compute a^b_min */
            int ndigits = 1;
            digits[0] = 1;
            for (int i = 0; i < b_min; i++) {
                bignum_mul(digits, &ndigits, a);
            }
            /* Store a^b_min */
            bignum_to_str(digits, ndigits, buf);
            hash_insert(buf);

            /* For each subsequent b, multiply by a */
            for (int b = b_min + 1; b <= b_max; b++) {
                bignum_mul(digits, &ndigits, a);
                bignum_to_str(digits, ndigits, buf);
                hash_insert(buf);
            }
        }
    } else {
        /* Prime signature approach */
        int primes[20], exponents[20];
        char buf[1024];

        for (int a = a_min; a <= a_max; a++) {
            int nfactors = prime_factorization(a, primes, exponents);
            for (int b = b_min; b <= b_max; b++) {
                /* Build signature string: "p1:e1*b,p2:e2*b,..." */
                int pos = 0;
                for (int j = 0; j < nfactors; j++) {
                    if (j > 0) buf[pos++] = ',';
                    pos += sprintf(buf + pos, "%d:%d", primes[j], exponents[j] * b);
                }
                buf[pos] = '\0';
                hash_insert(buf);
            }
        }
    }

    long long result = hash_count;
    hash_clear();
    return result;
}

/* Usage: ./file <kwarg>... [--runs=1] [--show]
 * Output: "<runs> <avg_seconds> <result>" */
int main(int argc, char *argv[]) {
    int runs = 1;

    char **solve_argv = malloc((size_t)argc * sizeof(char *));
    if (!solve_argv) {
        fprintf(stderr, "runner: out of memory\n");
        return 1;
    }
    int solve_argc = 0;
    solve_argv[solve_argc++] = argv[0];

    for (int i = 1; i < argc; i++) {
        if (argv[i][0] == '\0') continue;
        if (strncmp(argv[i], "--runs=", 7) == 0) {
            int r = atoi(argv[i] + 7);
            if (r >= 1) runs = r;
            continue;
        }
        if (strcmp(argv[i], "--show") == 0) continue;
        solve_argv[solve_argc++] = argv[i];
    }

    long long result = 0;
    double total = 0.0;
    int rc = 0;
    int has_result = 0;

    for (int r = 0; r < runs; r++) {
        struct timespec t0, t1;
        clock_gettime(CLOCK_MONOTONIC, &t0);
        long long cur = solve(solve_argc, solve_argv);
        clock_gettime(CLOCK_MONOTONIC, &t1);
        total += (double)(t1.tv_sec - t0.tv_sec)
               + (double)(t1.tv_nsec - t0.tv_nsec) * 1e-9;
        if (has_result && cur != result) {
            fprintf(stderr, "Expected consistent result, got %lld previous result=%lld\n",
                    cur, result);
            rc = 1;
        }
        result = cur;
        has_result = 1;
    }

    free(solve_argv);
    printf("%d %.17g %lld\n", runs, total / (double)runs, result);
    return rc;
}