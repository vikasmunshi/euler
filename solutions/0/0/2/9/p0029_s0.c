/* Solution to Euler Problem 29: Distinct Powers. */
#include "runner.h"

/* Trial-division factorization into (prime, exponent) pairs; O(sqrt(n)). */
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

/* Chained string-keyed hash set: each signature (or big-integer decimal)
   is encoded as a string key and deduplicated here. Power-of-two bucket
   count makes the index a bitwise AND rather than a modulo. */

#define HASH_SIZE (1 << 22)  /* 4M buckets */
#define HASH_MASK (HASH_SIZE - 1)

typedef struct HashNode {
    char *key;
    struct HashNode *next;
} HashNode;

static HashNode *hash_table[HASH_SIZE];
static int hash_count = 0;

/* Free every bucket chain and reset the element count. */
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

/* djb2 string hash, masked to the bucket range. */
static unsigned int hash_str(const char *s) {
    unsigned int h = 5381;
    while (*s) {
        h = ((h << 5) + h) + (unsigned char)*s;
        s++;
    }
    return h & HASH_MASK;
}

/* Insert key if absent; returns 1 if newly inserted, 0 if already present. */
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

/* Big integer in base 10^9, little-endian, used on the small-range path so
   a^b can be represented exactly (100^100 has about 200 decimal digits). */

#define BIGNUM_DIGITS 220

/* Multiply the big number in place by a small factor; the per-limb product
   plus carry is accumulated in a 64-bit value to avoid 32-bit overflow. */
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

/* Serialise the big number to a decimal string key: top limb unpadded,
   each remaining limb zero-padded to nine digits. */
static void bignum_to_str(int *digits, int ndigits, char *buf) {
    int pos = 0;
    pos += sprintf(buf + pos, "%d", digits[ndigits - 1]);
    for (int i = ndigits - 2; i >= 0; i--) {
        pos += sprintf(buf + pos, "%09d", digits[i]);
    }
    buf[pos] = '\0';
}

/* Count distinct values of a^b over the given ranges by deduplicating keys in
   a hash set; O(a_max * b_max) insertions dominate. Small bounds key on the
   exact big-integer decimal; large bounds key on the prime-factorization
   signature (prime, exponent*b), equal exactly when the powers are equal, so
   thousand-digit numbers are never built. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int a_min = parse_int(argv[1]);
    int a_max = parse_int(argv[2]);
    int b_min = parse_int(argv[3]);
    int b_max = parse_int(argv[4]);

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

            /* For each subsequent b, multiply by a (incremental exponentiation) */
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
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(result)); return _answer; }
}