/* Solution to Euler Problem 60: Prime Pair Sets. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <time.h>

/* Simple primality test */
static int is_prime(long long n) {
    if (n < 2) return 0;
    if (n == 2) return 1;
    if (n % 2 == 0) return 0;
    for (long long i = 3; i * i <= n; i += 2) {
        if (n % i == 0) return 0;
    }
    return 1;
}

/* Number of decimal digits in n */
static int num_digits(long long n) {
    if (n == 0) return 1;
    int d = 0;
    while (n > 0) { d++; n /= 10; }
    return d;
}

/* Concatenate a and b: e.g. a=3, b=7 -> 37 */
static long long concat(long long a, long long b) {
    int db = num_digits(b);
    long long mul = 1;
    for (int i = 0; i < db; i++) mul *= 10;
    return a * mul + b;
}

/* Check if concatenating a,b in both orders gives primes */
static int concatenate_is_prime(long long a, long long b) {
    return is_prime(concat(a, b)) && is_prime(concat(b, a));
}

/* --- Cache for pair results --- */
/* We use a hash table to cache results of concatenate_is_prime */

typedef struct CacheEntry {
    long long a, b;
    int result;
    struct CacheEntry *next;
} CacheEntry;

#define CACHE_SIZE (1 << 20)  /* 1M buckets */
static CacheEntry **cache_table = NULL;

static void cache_init(void) {
    cache_table = calloc(CACHE_SIZE, sizeof(CacheEntry *));
}

static void cache_free(void) {
    if (!cache_table) return;
    for (int i = 0; i < CACHE_SIZE; i++) {
        CacheEntry *e = cache_table[i];
        while (e) {
            CacheEntry *next = e->next;
            free(e);
            e = next;
        }
    }
    free(cache_table);
    cache_table = NULL;
}

static unsigned int cache_hash(long long a, long long b) {
    unsigned long long h = (unsigned long long)a * 1000003ULL ^ (unsigned long long)b;
    return (unsigned int)(h ^ (h >> 20) ^ (h >> 40)) & (CACHE_SIZE - 1);
}

/* Returns -1 if not found, else 0 or 1 */
static int cache_lookup(long long a, long long b) {
    unsigned int h = cache_hash(a, b);
    CacheEntry *e = cache_table[h];
    while (e) {
        if (e->a == a && e->b == b) return e->result;
        e = e->next;
    }
    return -1;
}

static void cache_insert(long long a, long long b, int result) {
    unsigned int h = cache_hash(a, b);
    CacheEntry *e = malloc(sizeof(CacheEntry));
    e->a = a;
    e->b = b;
    e->result = result;
    e->next = cache_table[h];
    cache_table[h] = e;
}

static int cached_concatenate_is_prime(long long a, long long b) {
    /* Canonicalize order for cache: use (min,max) key since concatenate_is_prime is symmetric */
    long long ka = a < b ? a : b;
    long long kb = a < b ? b : a;
    int r = cache_lookup(ka, kb);
    if (r >= 0) return r;
    r = concatenate_is_prime(a, b);
    cache_insert(ka, kb, r);
    return r;
}

/* Sieve of Sundaram */
static long long *sundaram_sieve(int max_num, int *count) {
    if (max_num < 2) { *count = 0; return NULL; }
    int n = (max_num - 1) / 2;
    char *marked = calloc((size_t)(n + 1), 1);
    for (int i = 1; i <= n; i++) {
        int j = i;
        while (i + j + 2 * i * j <= n) {
            marked[i + j + 2 * i * j] = 1;
            j++;
        }
    }
    /* Count primes */
    int cnt = (max_num >= 2) ? 1 : 0;
    for (int i = 1; i <= n; i++) {
        if (!marked[i]) cnt++;
    }
    long long *primes = malloc((size_t)cnt * sizeof(long long));
    int idx = 0;
    if (max_num >= 2) primes[idx++] = 2;
    for (int i = 1; i <= n; i++) {
        if (!marked[i]) primes[idx++] = 2 * i + 1;
    }
    free(marked);
    *count = cnt;
    return primes;
}

/* DFS clique search for set_length primes */
/* sol: current partial solution (ascending order)
   sol_size: number of elements in sol
   target: desired clique size
   primes: sorted prime array
   num_primes: length of primes
   start_idx: index in primes to start extending from */
static int found;
static long long best_sum;
static long long best_sol[10];
static int best_sol_size;

static void dfs(long long *sol, int sol_size, int target,
                long long *primes, int num_primes, int start_idx) {
    if (found) return;
    if (sol_size == target) {
        long long s = 0;
        for (int i = 0; i < sol_size; i++) { s += sol[i]; best_sol[i] = sol[i]; }
        best_sol_size = sol_size;
        best_sum = s;
        found = 1;
        return;
    }
    int need = target - sol_size;
    for (int i = start_idx; i <= num_primes - need; i++) {
        long long p = primes[i];
        /* Check p pairs with all existing elements */
        int ok = 1;
        for (int j = 0; j < sol_size; j++) {
            if (!cached_concatenate_is_prime(sol[j], p)) {
                ok = 0;
                break;
            }
        }
        if (ok) {
            sol[sol_size] = p;
            dfs(sol, sol_size + 1, target, primes, num_primes, i + 1);
            if (found) return;
        }
    }
}

long long solve(int argc, char *argv[], int show) {
    int set_length = 5;
    if (argc >= 2) set_length = atoi(argv[1]);

    /* Compute max prime: 10^(set_length-1) */
    int max_prime = 1;
    for (int i = 0; i < set_length - 1; i++) max_prime *= 10;

    cache_init();

    int num_primes = 0;
    long long *primes = sundaram_sieve(max_prime, &num_primes);

    found = 0;
    best_sum = 0;
    best_sol_size = 0;

    long long sol[10];
    /* For each prime as first element */
    for (int i = 0; i < num_primes && !found; i++) {
        sol[0] = primes[i];
        dfs(sol, 1, set_length, primes, num_primes, i + 1);
    }

    if (show && found) {
        printf("max prime = %lld num_primes = %d\n", primes[num_primes - 1], num_primes);
        printf("solution_list=[");
        for (int i = 0; i < best_sol_size; i++) {
            if (i > 0) printf(", ");
            printf("%lld", best_sol[i]);
        }
        printf("]\n");
        for (int i = 0; i < best_sol_size; i++) {
            for (int j = i + 1; j < best_sol_size; j++) {
                int r = cached_concatenate_is_prime(best_sol[i], best_sol[j]);
                printf("concatenate_prime(%lld, %lld)=%s\n",
                       best_sol[i], best_sol[j], r ? "True" : "False");
            }
        }
    }

    free(primes);
    cache_free();

    return best_sum;
}

/* Usage: ./file <set_length> [--runs=1] [--show]
 * Output: "<runs> <avg_seconds> <result>" */
int main(int argc, char *argv[]) {
    int runs = 1;
    int show = 0;

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
        if (strcmp(argv[i], "--show") == 0) { show = 1; continue; }
        solve_argv[solve_argc++] = argv[i];
    }

    long long result = 0;
    double total = 0.0;
    int rc = 0;
    int has_result = 0;

    for (int r = 0; r < runs; r++) {
        struct timespec t0, t1;
        clock_gettime(CLOCK_MONOTONIC, &t0);
        long long cur = solve(solve_argc, solve_argv, show);
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