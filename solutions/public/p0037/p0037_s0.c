/* Solution to Euler Problem 37: Truncatable Primes. */
#include "runner.h"

/* Incremental sieve using a hash map (open addressing) */

#define HASH_SIZE (1 << 20)  /* must be power of 2 */
#define HASH_MASK (HASH_SIZE - 1)

typedef struct {
    int key;   /* 0 = empty */
    int val;
} HashEntry;

static HashEntry htable[HASH_SIZE];

/* Insert key->val into the composites map (linear probing). */
static void hash_insert(int key, int val) {
    unsigned int h = (unsigned int)key & HASH_MASK;
    while (htable[h].key != 0 && htable[h].key != key)
        h = (h + 1) & HASH_MASK;
    htable[h].key = key;
    htable[h].val = val;
}

/* Return the stored value for key, or 0 if absent. */
static int hash_get(int key) {
    /* returns 0 if not found */
    unsigned int h = (unsigned int)key & HASH_MASK;
    while (htable[h].key != 0) {
        if (htable[h].key == key) return htable[h].val;
        h = (h + 1) & HASH_MASK;
    }
    return 0;
}

/* Test whether key is present in the composites map. */
static int hash_contains(int key) {
    unsigned int h = (unsigned int)key & HASH_MASK;
    while (htable[h].key != 0) {
        if (htable[h].key == key) return 1;
        h = (h + 1) & HASH_MASK;
    }
    return 0;
}

/* Delete key, then re-insert the contiguous probe chain so no lookup is broken. */
static void hash_remove(int key) {
    /* Robin Hood removal: mark slot and re-insert chain */
    unsigned int h = (unsigned int)key & HASH_MASK;
    while (htable[h].key != 0 && htable[h].key != key)
        h = (h + 1) & HASH_MASK;
    if (htable[h].key == 0) return;
    htable[h].key = 0;
    htable[h].val = 0;
    /* re-insert subsequent entries */
    unsigned int j = (h + 1) & HASH_MASK;
    while (htable[j].key != 0) {
        int k2 = htable[j].key, v2 = htable[j].val;
        htable[j].key = 0;
        htable[j].val = 0;
        hash_insert(k2, v2);
        j = (j + 1) & HASH_MASK;
    }
}

/* String set for prime strings using a separate hash table */

#define STR_HASH_SIZE (1 << 20)
#define STR_HASH_MASK (STR_HASH_SIZE - 1)

static char str_keys[STR_HASH_SIZE][12];  /* up to 11-digit numbers */
static int  str_used[STR_HASH_SIZE];

/* djb2 hash of a NUL-terminated prime string. */
static unsigned int str_hash(const char *s) {
    unsigned int h = 5381;
    while (*s) h = ((h << 5) + h) ^ (unsigned char)*s++;
    return h;
}

/* Insert a prime string into the seen-set (linear probing). */
static void str_set_insert(const char *s) {
    unsigned int h = str_hash(s) & STR_HASH_MASK;
    while (str_used[h] && strcmp(str_keys[h], s) != 0)
        h = (h + 1) & STR_HASH_MASK;
    str_used[h] = 1;
    strncpy(str_keys[h], s, 11);
    str_keys[h][11] = '\0';
}

/* Test whether a prime string is in the seen-set. */
static int str_set_contains(const char *s) {
    unsigned int h = str_hash(s) & STR_HASH_MASK;
    while (str_used[h]) {
        if (strcmp(str_keys[h], s) == 0) return 1;
        h = (h + 1) & STR_HASH_MASK;
    }
    return 0;
}

/* Stream primes as strings via an incremental sieve; a prime is truncatable iff every prefix and
   suffix already lies in the seen-set, so each test is O(digits) set lookups. Sorted generation
   guarantees those smaller primes are present; stop after the eleven known truncatable primes.
   Overall O(n log log n) over the range scanned. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    (void)argc; (void)argv;

    /* incremental sieve state */
    memset(htable, 0, sizeof(htable));
    memset(str_used, 0, sizeof(str_used));

    long long truncatable[11];
    int found = 0;
    long long total = 0;

    /* We implement the incremental sieve as in the Python solution.
       composites maps composite -> smallest prime factor.
       We iterate n starting at 3, step 2, having yielded 2 first. */

    /* yield 2 */
    str_set_insert("2");

    int n = 3;
    while (found < 11) {
        int is_prime = !hash_contains(n);
        if (is_prime) {
            /* yield n */
            char buf[16];
            snprintf(buf, sizeof(buf), "%d", n);
            str_set_insert(buf);

            /* insert n*n into composites */
            int nn = n * n;
            /* only if it fits (n < ~46340 for int); cast to long long guards the overflow check */
            if ((long long)n * n < (long long)(1 << 30)) {
                /* check n*n not already in map */
                if (!hash_contains(nn))
                    hash_insert(nn, n);
                /* else find next slot (the Python does m += 2*p while m in composites) */
                else {
                    int m = nn + 2 * n;
                    while (hash_contains(m)) m += 2 * n;
                    hash_insert(m, n);
                }
            }

            /* check if truncatable (2+ digits) */
            int len = (int)strlen(buf);
            if (len >= 2) {
                int ok = 1;
                for (int i = 1; i < len && ok; i++) {
                    /* right truncation: buf[:i] */
                    char left[12], right[12];
                    strncpy(left, buf, i);
                    left[i] = '\0';
                    /* left truncation: buf[i:] */
                    strncpy(right, buf + i, len - i);
                    right[len - i] = '\0';
                    if (!str_set_contains(left) || !str_set_contains(right))
                        ok = 0;
                }
                if (ok) {
                    truncatable[found++] = (long long)n;
                    total += (long long)n;
                }
            }
        } else {
            /* n is composite */
            int p = hash_get(n);
            hash_remove(n);
            int m = n + 2 * p;
            while (hash_contains(m)) m += 2 * p;
            hash_insert(m, p);
        }
        n += 2;
    }

    { snprintf(_answer, sizeof _answer, "%lld", (long long)(total)); return _answer; }
}