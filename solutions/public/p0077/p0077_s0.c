/* Solution to Euler Problem 77: Prime Summations. */
#include "runner.h"

/* Sieve of Sundaram: return primes up to max_num, writing the count via *count. */
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

/* Memoisation: key is (number, slots), value is the partition count.
 * Flat open-addressing hash table with linear probing for cache locality. */

#define MEMO_SIZE (1 << 18)  /* 262144 buckets */
#define MEMO_EMPTY (-1)

typedef struct {
    int number;
    int slots;
    long long value;
} MemoEntry;

static MemoEntry memo_table[MEMO_SIZE];
static int memo_initialized = 0;

/* Mark every bucket empty before first use. */
static void memo_init(void) {
    for (int i = 0; i < MEMO_SIZE; i++) {
        memo_table[i].number = MEMO_EMPTY;
        memo_table[i].slots  = MEMO_EMPTY;
        memo_table[i].value  = -1;
    }
    memo_initialized = 1;
}

/* Mix the two integer keys into a bucket index; power-of-two size lets % reduce to & . */
static unsigned int memo_hash(int number, int slots) {
    unsigned int h = (unsigned int)(number * 1000003 + slots);
    h ^= h >> 16;
    h *= 0x45d9f3b;
    h ^= h >> 16;
    return h & (MEMO_SIZE - 1);
}

/* Return the cached count for (number, slots), or -1 if absent. */
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

/* Store the count for (number, slots), overwriting any existing entry for that key. */
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

/* Count prime partitions of number using parts each at most slots; memoised recursion.
 * Passing the chosen prime p (not slots) as the next ceiling enforces non-increasing
 * parts, so each multiset is counted exactly once. */
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

/* Count-only memoised recursion over (remaining sum, max allowed part); first n whose
 * prime-partition count reaches the threshold. O(N * pi(N)) subproblems, O(pi(N)) each. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    if (argc < 2) { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    int threshold = parse_int(argv[1]);

    if (!memo_initialized) memo_init();

    for (int n = 1; ; n++) {
        long long count = num_prime_partitions(n, n);
        if (count >= threshold) { snprintf(_answer, sizeof _answer, "%lld", (long long)(n)); return _answer; }
    }
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
}