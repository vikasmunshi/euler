/* Solution to Euler Problem 49: Prime Permutations. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static int *primes_sundaram_sieve(int max_num, int *out_count) {
    *out_count = 0;
    if (max_num < 2) return NULL;
    int n = (max_num - 1) / 2;
    unsigned char *marked = calloc((size_t)(n + 1), 1);
    if (!marked) return NULL;
    for (int i = 1; i <= n; i++) {
        for (int j = i; (long long)i + j + 2LL * i * j <= n; j++) {
            marked[i + j + 2 * i * j] = 1;
        }
    }
    int cap = 1024;
    int *primes = malloc((size_t)cap * sizeof(int));
    if (!primes) { free(marked); return NULL; }
    if (max_num >= 2) {
        if (*out_count >= cap) { cap *= 2; primes = realloc(primes, (size_t)cap * sizeof(int)); }
        primes[(*out_count)++] = 2;
    }
    for (int i = 1; i <= n; i++) {
        if (!marked[i]) {
            if (*out_count >= cap) { cap *= 2; primes = realloc(primes, (size_t)cap * sizeof(int)); }
            primes[(*out_count)++] = 2 * i + 1;
        }
    }
    free(marked);
    return primes;
}

static int cmp_int(const void *a, const void *b) {
    return (*(int*)a) - (*(int*)b);
}

static int cmp_str(const void *a, const void *b) {
    return strcmp(*(const char**)a, *(const char**)b);
}

/* Heap's algorithm: generate all permutations of s[0..len-1].
   results is a 2D array of char[16]. Returns count. */
static int permute(char *s, int len, char *results, int stride, int max_results) {
    int count = 0;
    int *c = calloc((size_t)len, sizeof(int));
    if (!c) return 0;
    if (count < max_results) {
        memcpy(results + count * stride, s, (size_t)(len + 1));
        count++;
    }
    int i = 0;
    while (i < len) {
        if (c[i] < i) {
            if (i % 2 == 0) {
                char tmp = s[0]; s[0] = s[i]; s[i] = tmp;
            } else {
                char tmp = s[c[i]]; s[c[i]] = s[i]; s[i] = tmp;
            }
            if (count < max_results) {
                memcpy(results + count * stride, s, (size_t)(len + 1));
                count++;
            }
            c[i]++;
            i = 0;
        } else {
            c[i] = 0;
            i++;
        }
    }
    free(c);
    return count;
}

static int in_sorted_str_array(char **arr, int size, const char *key) {
    int lo = 0, hi = size - 1;
    while (lo <= hi) {
        int mid = (lo + hi) / 2;
        int cmp = strcmp(arr[mid], key);
        if (cmp == 0) return 1;
        else if (cmp < 0) lo = mid + 1;
        else hi = mid - 1;
    }
    return 0;
}

static int seq_in_results(char **results, int count, const char *s) {
    for (int i = 0; i < count; i++)
        if (strcmp(results[i], s) == 0) return 1;
    return 0;
}

char *solve(int argc, char *argv[]) {
    int n = (argc > 1) ? atoi(argv[1]) : 4;

    int min_n_digit = 1;
    for (int i = 0; i < n - 1; i++) min_n_digit *= 10;
    int max_n_digit = min_n_digit * 10;

    int prime_count = 0;
    int *all_primes = primes_sundaram_sieve(max_n_digit, &prime_count);

    int nd_count = 0;
    int nd_cap = 4096;
    char **nd_primes = malloc((size_t)nd_cap * sizeof(char *));

    for (int i = 0; i < prime_count; i++) {
        if (all_primes[i] > min_n_digit) {
            if (nd_count >= nd_cap) {
                nd_cap *= 2;
                nd_primes = realloc(nd_primes, (size_t)nd_cap * sizeof(char *));
            }
            char buf[16];
            snprintf(buf, sizeof(buf), "%d", all_primes[i]);
            nd_primes[nd_count++] = strdup(buf);
        }
    }
    free(all_primes);

    qsort(nd_primes, (size_t)nd_count, sizeof(char *), cmp_str);

    int res_cap = 256;
    int res_count = 0;
    char **sequences = malloc((size_t)res_cap * sizeof(char *));

    /* max permutations: n! */
    int max_perms = 1;
    for (int i = 1; i <= n; i++) max_perms *= i;

    int stride = 16;
    char *perm_buf = malloc((size_t)(max_perms * stride));

    for (int pi = 0; pi < nd_count; pi++) {
        const char *prime_str = nd_primes[pi];
        int plen = (int)strlen(prime_str);

        char work[16];
        strncpy(work, prime_str, 15);
        work[15] = '\0';

        int np = permute(work, plen, perm_buf, stride, max_perms);

        /* Collect unique prime siblings */
        int sib_cap = max_perms + 4;
        int sib_count = 0;
        int *sibs = malloc((size_t)sib_cap * sizeof(int));

        for (int p2 = 0; p2 < np; p2++) {
            char *perm = perm_buf + p2 * stride;
            if (perm[0] == '0') continue;
            if (!in_sorted_str_array(nd_primes, nd_count, perm)) continue;
            int val = atoi(perm);
            int dup = 0;
            for (int k = 0; k < sib_count; k++) {
                if (sibs[k] == val) { dup = 1; break; }
            }
            if (!dup) {
                sibs[sib_count++] = val;
            }
        }

        if (sib_count < 3) { free(sibs); continue; }

        qsort(sibs, (size_t)sib_count, sizeof(int), cmp_int);

        /* Difference bucketing */
        /* max unique differences = C(sib_count, 2) */
        int max_diffs = sib_count * (sib_count - 1) / 2 + 1;
        int *diff_keys = malloc((size_t)max_diffs * sizeof(int));
        /* Each diff bucket: store up to sib_count values */
        int *diff_set_counts = calloc((size_t)max_diffs, sizeof(int));
        /* Flat storage: diff_sets_data[bucket_idx][value_idx] */
        int *diff_sets_data = malloc((size_t)(max_diffs * sib_count) * sizeof(int));
        int diff_count = 0;

        for (int a = 0; a < sib_count - 1; a++) {
            for (int b = a + 1; b < sib_count; b++) {
                int diff = sibs[b] - sibs[a];
                int found = -1;
                for (int k = 0; k < diff_count; k++) {
                    if (diff_keys[k] == diff) { found = k; break; }
                }
                if (found == -1) {
                    if (diff_count < max_diffs) {
                        diff_keys[diff_count] = diff;
                        diff_set_counts[diff_count] = 0;
                        found = diff_count++;
                    } else {
                        continue;
                    }
                }
                int *bucket = diff_sets_data + found * sib_count;
                int bcount = diff_set_counts[found];
                for (int v = 0; v < 2; v++) {
                    int val = (v == 0) ? sibs[a] : sibs[b];
                    int dup = 0;
                    for (int k = 0; k < bcount; k++) {
                        if (bucket[k] == val) { dup = 1; break; }
                    }
                    if (!dup && bcount < sib_count) {
                        bucket[bcount++] = val;
                    }
                }
                diff_set_counts[found] = bcount;
            }
        }

        for (int k = 0; k < diff_count; k++) {
            if (diff_set_counts[k] == 3) {
                int *trio = diff_sets_data + k * sib_count;
                /* Sort trio */
                int t0 = trio[0], t1 = trio[1], t2 = trio[2];
                if (t0 > t1) { int t = t0; t0 = t1; t1 = t; }
                if (t1 > t2) { int t = t1; t1 = t2; t2 = t; }
                if (t0 > t1) { int t = t0; t0 = t1; t1 = t; }

                char seq[64];
                snprintf(seq, sizeof(seq), "%d %d %d", t0, t1, t2);
                if (!seq_in_results(sequences, res_count, seq)) {
                    if (res_count >= res_cap) {
                        res_cap *= 2;
                        sequences = realloc(sequences, (size_t)res_cap * sizeof(char *));
                    }
                    sequences[res_count++] = strdup(seq);
                }
            }
        }

        free(diff_keys);
        free(diff_set_counts);
        free(diff_sets_data);
        free(sibs);
    }

    free(perm_buf);
    for (int i = 0; i < nd_count; i++) free(nd_primes[i]);
    free(nd_primes);

    qsort(sequences, (size_t)res_count, sizeof(char *), cmp_str);

    /* Build JSON-style array string with single quotes */
    size_t total_len = 3;
    for (int i = 0; i < res_count; i++) total_len += strlen(sequences[i]) + 6;
    char *result = malloc(total_len);
    int pos = 0;
    result[pos++] = '[';
    for (int i = 0; i < res_count; i++) {
        if (i > 0) { result[pos++] = ','; result[pos++] = ' '; }
        result[pos++] = '\'';
        int slen = (int)strlen(sequences[i]);
        memcpy(result + pos, sequences[i], (size_t)slen);
        pos += slen;
        result[pos++] = '\'';
    }
    result[pos++] = ']';
    result[pos] = '\0';

    for (int i = 0; i < res_count; i++) free(sequences[i]);
    free(sequences);

    return result;
}

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

    char *result = NULL;
    double total = 0.0;
    int rc = 0;

    for (int r = 0; r < runs; r++) {
        struct timespec t0, t1;
        clock_gettime(CLOCK_MONOTONIC, &t0);
        char *cur = solve(solve_argc, solve_argv);
        clock_gettime(CLOCK_MONOTONIC, &t1);
        total += (double)(t1.tv_sec - t0.tv_sec)
               + (double)(t1.tv_nsec - t0.tv_nsec) * 1e-9;
        if (result) {
            if (strcmp(cur, result) != 0) {
                fprintf(stderr, "Expected consistent result, got %s previous result=%s\n",
                        cur, result);
                rc = 1;
            }
            free(cur);
        } else {
            result = cur;
        }
    }

    free(solve_argv);
    printf("%d %.17g %s\n", runs, total / (double)runs, result ? result : "[]");
    free(result);
    return rc;
}