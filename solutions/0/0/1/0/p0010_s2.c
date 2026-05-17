/* Solution to Euler Problem 10: Summation of Primes. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

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

long long solve(int argc, char *argv[]) {
    int max_num = atoi(argv[1]);
    if (max_num <= 2) return (max_num == 2) ? 0 : 0;

    long long result = 0;
    HTable *composites = htable_new(HTABLE_INIT_CAP);
    if (!composites) return -1;

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