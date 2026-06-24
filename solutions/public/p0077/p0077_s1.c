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

/* A partition is stored as an array of ints with a length field */
typedef struct {
    int *parts;
    int  len;
} Partition;

/* A list of partitions */
typedef struct {
    Partition *items;
    int        count;
    int        cap;
} PartList;

/* Return an empty PartList. */
static PartList make_part_list(void) {
    PartList pl;
    pl.items = NULL;
    pl.count = 0;
    pl.cap   = 0;
    return pl;
}

/* Free every partition array and the items buffer, then reset the list. */
static void part_list_free(PartList *pl) {
    for (int i = 0; i < pl->count; i++) {
        free(pl->items[i].parts);
    }
    free(pl->items);
    pl->items = NULL;
    pl->count = 0;
    pl->cap   = 0;
}

/* Memo for partition enumeration: keyed by (number, slots), value is the owned PartList. */
#define ENUM_MEMO_SIZE (1 << 14)  /* 16384 buckets */

typedef struct EnumMemoEntry {
    int number;
    int slots;
    PartList pl;
    int valid;
} EnumMemoEntry;

static EnumMemoEntry enum_memo[ENUM_MEMO_SIZE];
static int enum_memo_initialized = 0;

/* Free all owned PartLists and mark every bucket empty before first use. */
static void enum_memo_init(void) {
    for (int i = 0; i < ENUM_MEMO_SIZE; i++) {
        if (enum_memo[i].valid) {
            part_list_free(&enum_memo[i].pl);
        }
        enum_memo[i].number = -1;
        enum_memo[i].slots  = -1;
        enum_memo[i].valid  = 0;
    }
    enum_memo_initialized = 1;
}

/* Mix the two integer keys into a bucket index; power-of-two size lets % reduce to & . */
static unsigned int enum_hash(int number, int slots) {
    unsigned int h = (unsigned int)(number * 1000003 + slots);
    h ^= h >> 16;
    h *= 0x45d9f3b;
    h ^= h >> 16;
    return h & (ENUM_MEMO_SIZE - 1);
}

/* Return a pointer to the cached PartList for (number, slots), or NULL if absent. */
static PartList *enum_memo_get(int number, int slots) {
    unsigned int idx = enum_hash(number, slots);
    for (int probe = 0; probe < ENUM_MEMO_SIZE; probe++) {
        unsigned int i = (idx + (unsigned int)probe) & (ENUM_MEMO_SIZE - 1);
        if (!enum_memo[i].valid) return NULL;
        if (enum_memo[i].number == number && enum_memo[i].slots == slots)
            return &enum_memo[i].pl;
    }
    return NULL;
}

/* Store pl for (number, slots), taking ownership of its arrays and freeing any prior entry. */
static void enum_memo_set(int number, int slots, PartList *pl) {
    unsigned int idx = enum_hash(number, slots);
    for (int probe = 0; probe < ENUM_MEMO_SIZE; probe++) {
        unsigned int i = (idx + (unsigned int)probe) & (ENUM_MEMO_SIZE - 1);
        if (!enum_memo[i].valid) {
            enum_memo[i].number = number;
            enum_memo[i].slots  = slots;
            enum_memo[i].pl     = *pl;
            enum_memo[i].valid  = 1;
            return;
        }
        if (enum_memo[i].number == number && enum_memo[i].slots == slots) {
            part_list_free(&enum_memo[i].pl);
            enum_memo[i].pl = *pl;
            return;
        }
    }
}

/* safe_limit: beyond this the partition count explodes; set large enough for all test cases */
static int g_safe_limit = 50;

/* Build every prime partition of number with parts <= slots, prepending each chosen prime p
 * to the sub-partitions of the remainder; p is also the next ceiling, forcing non-increasing
 * parts. Returns NULL on overflow (number > safe_limit), else an owned PartList in the memo. */
static PartList *get_prime_partitions(int number, int slots) {
    if (number > g_safe_limit) return NULL;  /* overflow guard */

    if (number < 2 || slots < 2) {
        PartList *cached = enum_memo_get(number, slots);
        if (cached) return cached;
        PartList empty = make_part_list();
        enum_memo_set(number, slots, &empty);
        return enum_memo_get(number, slots);
    }

    PartList *cached = enum_memo_get(number, slots);
    if (cached) return cached;

    PartList result = make_part_list();
    int max_num = number < slots ? number : slots;
    int pcount = 0;
    int *primes = sundaram_sieve(max_num, &pcount);

    if (primes) {
        for (int pi = 0; pi < pcount; pi++) {
            int p = primes[pi];
            if (p > max_num) break;
            if (p == number) {
                /* Single prime partition */
                if (result.count == result.cap) {
                    int new_cap = result.cap == 0 ? 8 : result.cap * 2;
                    result.items = realloc(result.items, (size_t)new_cap * sizeof(Partition));
                    result.cap = new_cap;
                }
                int *single = malloc(sizeof(int));
                single[0] = p;
                result.items[result.count].parts = single;
                result.items[result.count].len   = 1;
                result.count++;
            } else {
                int rem = number - p;
                int new_slots = rem < p ? rem : p;
                PartList *sub = get_prime_partitions(rem, new_slots);
                if (!sub) {
                    /* overflow propagation */
                    part_list_free(&result);
                    free(primes);
                    return NULL;
                }
                /* Prepend p to each sub-partition */
                for (int j = 0; j < sub->count; j++) {
                    int new_len = sub->items[j].len + 1;
                    int *new_parts = malloc((size_t)new_len * sizeof(int));
                    new_parts[0] = p;
                    memcpy(new_parts + 1, sub->items[j].parts,
                           (size_t)sub->items[j].len * sizeof(int));
                    /* Grow by doubling for amortised O(1) append. */
                    if (result.count == result.cap) {
                        int new_cap = result.cap == 0 ? 8 : result.cap * 2;
                        result.items = realloc(result.items, (size_t)new_cap * sizeof(Partition));
                        result.cap = new_cap;
                    }
                    result.items[result.count].parts = new_parts;
                    result.items[result.count].len   = new_len;
                    result.count++;
                }
            }
        }
        free(primes);
    }

    enum_memo_set(number, slots, &result);
    return enum_memo_get(number, slots);
}

/* Enumeration-based memoised recursion: build all prime partitions and take the length of the
 * first n whose list reaches the threshold. Far slower than the count-only sibling because it
 * allocates and copies O(count) int arrays per subproblem; g_safe_limit bounds the search. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    if (argc < 2) { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    int threshold = parse_int(argv[1]);

    if (!enum_memo_initialized) enum_memo_init();

    /* Determine safe_limit: we need enough room to find the answer.
     * Search upward until we find the answer or hit the safe_limit.
     * Use a generous limit: 200 is large enough for all provided test cases. */
    g_safe_limit = 200;

    for (int n = 2; n <= g_safe_limit; n++) {
        PartList *pl = get_prime_partitions(n, n);
        if (!pl) {
            fprintf(stderr, "OverflowError: number exceeds safe_limit=%d\n", g_safe_limit);
            { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
        }
        if (pl->count >= threshold) { snprintf(_answer, sizeof _answer, "%lld", (long long)(n)); return _answer; }
    }

    fprintf(stderr, "OverflowError: answer exceeds safe_limit=%d\n", g_safe_limit);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
}