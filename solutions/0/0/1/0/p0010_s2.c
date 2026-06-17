/* Solution to Euler Problem 10: Summation of Primes. */
#include "runner.h"

/*
 * Incremental dictionary-based prime generator translated to C.
 * We use a hash map (open addressing) mapping composite -> prime that generated it.
 */

#define HTABLE_INIT_CAP 1024

typedef struct {
    long long key;
    long long value;
    int used;
} HEntry;

typedef struct {
    HEntry *entries;
    size_t cap;
    size_t count;
} HTable;

static HTable *htable_new(size_t cap) {
    HTable *ht = malloc(sizeof(HTable));
    if (!ht) return NULL;
    ht->entries = calloc(cap, sizeof(HEntry));
    if (!ht->entries) { free(ht); return NULL; }
    ht->cap = cap;
    ht->count = 0;
    return ht;
}

static void htable_free(HTable *ht) {
    free(ht->entries);
    free(ht);
}

static size_t htable_slot(HTable *ht, long long key) {
    /* FNV-inspired mix */
    unsigned long long h = (unsigned long long)key * 2654435761ULL;
    return (size_t)(h % ht->cap);
}

static int htable_get(HTable *ht, long long key, long long *val) {
    size_t idx = htable_slot(ht, key);
    size_t probe = 0;
    while (probe < ht->cap) {
        HEntry *e = &ht->entries[idx];
        if (!e->used) return 0;
        if (e->key == key) { *val = e->value; return 1; }
        idx = (idx + 1) % ht->cap;
        probe++;
    }
    return 0;
}

static void htable_grow(HTable *ht);

static void htable_set(HTable *ht, long long key, long long value) {
    if (ht->count * 2 >= ht->cap) htable_grow(ht);
    size_t idx = htable_slot(ht, key);
    while (1) {
        HEntry *e = &ht->entries[idx];
        if (!e->used) {
            e->key = key; e->value = value; e->used = 1;
            ht->count++;
            return;
        }
        if (e->key == key) { e->value = value; return; }
        idx = (idx + 1) % ht->cap;
    }
}

static int htable_del(HTable *ht, long long key, long long *val) {
    size_t idx = htable_slot(ht, key);
    size_t probe = 0;
    while (probe < ht->cap) {
        HEntry *e = &ht->entries[idx];
        if (!e->used) return 0;
        if (e->key == key) {
            *val = e->value;
            e->used = 0;
            ht->count--;
            /* Rehash subsequent entries in the cluster */
            size_t j = (idx + 1) % ht->cap;
            while (ht->entries[j].used) {
                HEntry tmp = ht->entries[j];
                ht->entries[j].used = 0;
                ht->count--;
                htable_set(ht, tmp.key, tmp.value);
                j = (j + 1) % ht->cap;
            }
            return 1;
        }
        idx = (idx + 1) % ht->cap;
        probe++;
    }
    return 0;
}

static void htable_grow(HTable *ht) {
    size_t new_cap = ht->cap * 2;
    HEntry *old = ht->entries;
    size_t old_cap = ht->cap;
    ht->entries = calloc(new_cap, sizeof(HEntry));
    ht->cap = new_cap;
    ht->count = 0;
    for (size_t i = 0; i < old_cap; i++) {
        if (old[i].used) htable_set(ht, old[i].key, old[i].value);
    }
    free(old);
}

/* Sum primes below max_num from an unbounded incremental Sieve of Eratosthenes; O(n log log n). */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int max_num = parse_int(argv[1]);
    if (max_num <= 2) { snprintf(_answer, sizeof _answer, "%lld", (long long)((max_num == 2) ? 0 : 0)); return _answer; }

    long long result = 0;
    HTable *composites = htable_new(HTABLE_INIT_CAP);
    if (!composites) { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }

    /* yield 2 first */
    if (2 < max_num) result += 2;

    long long n = 3;
    while (n < max_num) {
        long long p;
        if (!htable_get(composites, n, &p)) {
            /* n is prime */
            result += n;
            htable_set(composites, n * n, n);
        } else {
            htable_del(composites, n, &p);
            long long m = n + 2 * p;
            long long dummy;
            while (htable_get(composites, m, &dummy)) {
                m += 2 * p;
            }
            htable_set(composites, m, p);
        }
        n += 2;
    }

    htable_free(composites);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(result)); return _answer; }
}
