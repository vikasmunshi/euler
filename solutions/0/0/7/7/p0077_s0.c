/* Solution to Euler Problem 77: Prime Summations. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

/* Sieve of Sundaram: return primes up to max_num */
static int *sundaram_sieve(int max_num, int *count) {
    *count = 0;
    if (max_num < 2) return NULL;
    int n = (max_num - 1) / 2;
    char *marked = calloc((size_t)(n + 1), 1);
    if (!marked) return NULL;
    for (int i = 1; i <= n; i++) {
        for (int j = i; i + j + 2 * i * j <= n; j++) {
            marked[i + j + 2 * i * j] = 1;
        }
    }
    /* count primes */
    int cap = 1;
    for (int i = 1; i <= n; i++) if (!marked[i]) cap++;
    int *primes = malloc((size_t)cap * sizeof(int));
    if (!primes) { free(marked); return NULL; }
    primes[(*count)++] = 2;
    for (int i = 1; i <= n; i++) {
        if (!marked[i]) primes[(*count)++] = 2 * i + 1;
    }
    free(marked);
    return primes;
}

/* Memoisation: key is (number, slots), value is count */
/* Use a hash map with open addressing */

#define MEMO_SIZE (1 << 18)  /* 262144 buckets */
#define MEMO_EMPTY (-1)

typedef struct {
    int number;
    int slots;
    long long value;
} MemoEntry;

static MemoEntry memo_table[MEMO_SIZE];
static int memo_initialized = 0;

static void memo_init(void) {
    for (int i = 0; i < MEMO_SIZE; i++) {
        memo_table[i].number = MEMO_EMPTY;
        memo_table[i].slots  = MEMO_EMPTY;
        memo_table[i].value  = -1;
    }
    memo_initialized = 1;
}

static unsigned int memo_hash(int number, int slots) {
    unsigned int h = (unsigned int)(number * 1000003 + slots);
    h ^= h >> 16;
    h *= 0x45d9f3b;
    h ^= h >> 16;
    return h & (MEMO_SIZE - 1);
}

static long long memo_get(int number, int slots) {
    unsigned int idx = memo_hash(number, slots);
    for (int probe = 0; probe < MEMO_SIZE; probe++) {
        unsigned int i = (idx + (unsigned int)probe) & (MEMO_SIZE - 1);
        if (memo_table[i].number == MEMO_EMPTY) return -1;
        if (memo_table[i].number == number && memo_table[i].slots == slots)
            return memo_table[i].value;
    }
    return -1;
}

static void memo_set(int number, int slots, long long value) {
    unsigned int idx = memo_hash(number, slots);
    for (int probe = 0; probe < MEMO_SIZE; probe++) {
        unsigned int i = (idx + (unsigned int)probe) & (MEMO_SIZE - 1);
        if (memo_table[i].number == MEMO_EMPTY ||
            (memo_table[i].number == number && memo_table[i].slots == slots)) {
            memo_table[i].number = number;
            memo_table[i].slots  = slots;
            memo_table[i].value  = value;
            return;
        }
    }
}

static long long num_prime_partitions(int number, int slots) {
    if (number == 0) return 1;
    if (slots < 2)   return 0;

    long long cached = memo_get(number, slots);
    if (cached >= 0) return cached;

    long long result = 0;
    int max_num = number < slots ? number : slots;
    int pcount = 0;
    int *primes = sundaram_sieve(max_num, &pcount);
    if (primes) {
        for (int i = 0; i < pcount; i++) {
            int p = primes[i];
            if (p > max_num) break;
            result += num_prime_partitions(number - p, p);
        }
        free(primes);
    }

    memo_set(number, slots, result);
    return result;
}

long long solve(int argc, char *argv[]) {
    if (argc < 2) return -1;
    int threshold = atoi(argv[1]);

    if (!memo_initialized) memo_init();

    for (int n = 1; ; n++) {
        long long count = num_prime_partitions(n, n);
        if (count >= threshold) return n;
    }
    return -1;
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
        /* Reset memo for each run */
        memo_init();
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