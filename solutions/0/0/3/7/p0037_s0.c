/* Solution to Euler Problem 37: Truncatable Primes. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

/* Incremental sieve using a hash map (open addressing) */

#define HASH_SIZE (1 << 20)  /* must be power of 2 */
#define HASH_MASK (HASH_SIZE - 1)

typedef struct {
    int key;   /* 0 = empty */
    int val;
} HashEntry;

static HashEntry htable[HASH_SIZE];

static void hash_insert(int key, int val) {
    unsigned int h = (unsigned int)key & HASH_MASK;
    while (htable[h].key != 0 && htable[h].key != key)
        h = (h + 1) & HASH_MASK;
    htable[h].key = key;
    htable[h].val = val;
}

static int hash_get(int key) {
    /* returns 0 if not found */
    unsigned int h = (unsigned int)key & HASH_MASK;
    while (htable[h].key != 0) {
        if (htable[h].key == key) return htable[h].val;
        h = (h + 1) & HASH_MASK;
    }
    return 0;
}

static int hash_contains(int key) {
    unsigned int h = (unsigned int)key & HASH_MASK;
    while (htable[h].key != 0) {
        if (htable[h].key == key) return 1;
        h = (h + 1) & HASH_MASK;
    }
    return 0;
}

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

static unsigned int str_hash(const char *s) {
    unsigned int h = 5381;
    while (*s) h = ((h << 5) + h) ^ (unsigned char)*s++;
    return h;
}

static void str_set_insert(const char *s) {
    unsigned int h = str_hash(s) & STR_HASH_MASK;
    while (str_used[h] && strcmp(str_keys[h], s) != 0)
        h = (h + 1) & STR_HASH_MASK;
    str_used[h] = 1;
    strncpy(str_keys[h], s, 11);
    str_keys[h][11] = '\0';
}

static int str_set_contains(const char *s) {
    unsigned int h = str_hash(s) & STR_HASH_MASK;
    while (str_used[h]) {
        if (strcmp(str_keys[h], s) == 0) return 1;
        h = (h + 1) & STR_HASH_MASK;
    }
    return 0;
}

long long solve(int argc, char *argv[]) {
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
            /* only if it fits (n < ~46340 for int) */
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

    return total;
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
        /* reset global state for each run */
        memset(htable, 0, sizeof(htable));
        memset(str_used, 0, sizeof(str_used));

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