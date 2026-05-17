/* Solution to Euler Problem 62: Cubic Permutations. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <time.h>

/* Compare function for qsort on chars */
static int char_cmp(const void *a, const void *b) {
    return (*(const char *)a) - (*(const char *)b);
}

/* Compute sorted-digit string of n into buf (must be large enough) */
static void sorted_digits(long long n, char *buf) {
    char tmp[32];
    snprintf(tmp, sizeof(tmp), "%lld", n);
    strcpy(buf, tmp);
    qsort(buf, strlen(buf), 1, char_cmp);
}

/* Simple hash map entry */
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

static unsigned int hash_str(const char *s) {
    unsigned int h = 5381;
    while (*s) {
        h = ((h << 5) + h) + (unsigned char)(*s++);
    }
    return h & (HASH_SIZE - 1);
}

static HashMap *hashmap_create(void) {
    HashMap *m = calloc(1, sizeof(HashMap));
    return m;
}

static void hashmap_insert(HashMap *m, const char *key, long long value) {
    unsigned int h = hash_str(key);
    Entry *e = m->buckets[h];
    while (e) {
        if (strcmp(e->key, key) == 0) {
            if (e->count >= e->capacity) {
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

long long solve(int argc, char *argv[]) {
    int num_permutations = (argc >= 2) ? atoi(argv[1]) : 5;

    int digit_length = 2;

    while (1) {
        /* Compute start and stop ranges for cubes with digit_length digits */
        /* start_range = ceil((10^(digit_length-1))^(1/3)) */
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
            return best;
        }

        digit_length++;
    }
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