/* Solution to Euler Problem 62: Cubic Permutations. */
#include "runner.h"
#include <math.h>

/*
 * Approach: process cubes one digit-length band at a time (permutations share
 * a digit count), grouping each cube by its sorted-digit string - a canonical
 * key identical for every digit-permutation. The first band with a group of
 * exactly num_permutations cubes yields the smallest such cube. For a band of
 * d digits there are ~10^(d/3) cubes, each costing O(d log d) to key, so the
 * total is O(10^(d/3) * d log d) up to the answer's length.
 */

/* Comparator for qsort to order chars (digits) ascending. */
static int char_cmp(const void *a, const void *b) {
    return (*(const char *)a) - (*(const char *)b);
}

/* Write the ascending-sorted decimal digits of n into buf as the canonical key. */
static void sorted_digits(long long n, char *buf) {
    char tmp[32];
    snprintf(tmp, sizeof(tmp), "%lld", n);
    strcpy(buf, tmp);
    qsort(buf, strlen(buf), 1, char_cmp);
}

/* Hash-map entry: a canonical key and its amortised-doubling list of cubes. */
typedef struct Entry {
    char key[32];          /* sorted-digit string */
    long long *values;     /* list of cube values */
    int count;
    int capacity;
    struct Entry *next;
} Entry;

#define HASH_SIZE 65536

typedef struct {
    Entry *buckets[HASH_SIZE];
} HashMap;

/* djb2 string hash reduced to a bucket index via bitwise AND (power-of-two size). */
static unsigned int hash_str(const char *s) {
    unsigned int h = 5381;
    while (*s) {
        h = ((h << 5) + h) + (unsigned char)(*s++);
    }
    return h & (HASH_SIZE - 1);
}

/* Allocate a zero-initialised hash map. */
static HashMap *hashmap_create(void) {
    HashMap *m = calloc(1, sizeof(HashMap));
    return m;
}

/* Append value to the list keyed by key, creating the entry if absent. */
static void hashmap_insert(HashMap *m, const char *key, long long value) {
    unsigned int h = hash_str(key);
    Entry *e = m->buckets[h];
    while (e) {
        if (strcmp(e->key, key) == 0) {
            if (e->count >= e->capacity) {
                /* Amortised doubling keeps append O(1) amortised. */
                e->capacity = e->capacity ? e->capacity * 2 : 4;
                e->values = realloc(e->values, (size_t)e->capacity * sizeof(long long));
            }
            e->values[e->count++] = value;
            return;
        }
        e = e->next;
    }
    /* new entry */
    Entry *ne = calloc(1, sizeof(Entry));
    strncpy(ne->key, key, sizeof(ne->key) - 1);
    ne->capacity = 4;
    ne->values = malloc((size_t)ne->capacity * sizeof(long long));
    ne->values[0] = value;
    ne->count = 1;
    ne->next = m->buckets[h];
    m->buckets[h] = ne;
}

/* Free every entry, its value array, and the map itself. */
static void hashmap_free(HashMap *m) {
    for (int i = 0; i < HASH_SIZE; i++) {
        Entry *e = m->buckets[i];
        while (e) {
            Entry *next = e->next;
            free(e->values);
            free(e);
            e = next;
        }
    }
    free(m);
}

const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int num_permutations = (argc >= 2) ? parse_int(argv[1]) : 5;

    int digit_length = 2;

    while (1) {
        /* Compute start and stop ranges for cubes with digit_length digits */
        /* start_range = ceil((10^(digit_length-1))^(1/3)) */
        /* ceil on the lower bound avoids floating-point underestimation of an */
        /* exact cube root pulling in a cube from the wrong digit band. */
        double lo = pow(10.0, digit_length - 1);
        double hi = pow(10.0, digit_length) - 1.0;

        long long start_range = (long long)ceil(cbrt(lo));
        long long stop_range  = (long long)ceil(cbrt(hi)) + 1;

        HashMap *permuted_cubes = hashmap_create();

        for (long long i = start_range; i < stop_range; i++) {
            long long cube = i * i * i;
            char key[32];
            sorted_digits(cube, key);
            hashmap_insert(permuted_cubes, key, cube);
        }

        /* Find groups with exactly num_permutations members */
        long long best = -1;
        for (int b = 0; b < HASH_SIZE; b++) {
            Entry *e = permuted_cubes->buckets[b];
            while (e) {
                if (e->count == num_permutations) {
                    /* find minimum cube in this group */
                    long long mn = e->values[0];
                    for (int j = 1; j < e->count; j++) {
                        if (e->values[j] < mn) mn = e->values[j];
                    }
                    if (best < 0 || mn < best) best = mn;
                }
                e = e->next;
            }
        }

        hashmap_free(permuted_cubes);

        if (best >= 0) {
            { snprintf(_answer, sizeof _answer, "%lld", (long long)(best)); return _answer; }
        }

        digit_length++;
    }
}