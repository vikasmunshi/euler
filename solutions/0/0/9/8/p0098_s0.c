/* Solution to Euler Problem 98: Anagramic Squares. */
#include <libgen.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

char *get_text_file(const char *src) {
    const char *slash = strrchr(src, '/');
    const char *name_start = slash ? slash + 1 : src;
    const char *q = strchr(name_start, '?');
    size_t name_len = q ? (size_t)(q - name_start) : strlen(name_start);

    char exe_path[4096];
    ssize_t len = readlink("/proc/self/exe", exe_path, sizeof(exe_path) - 1);
    if (len < 0) return NULL;
    exe_path[len] = '\0';

    char path[4096];
    int pn = snprintf(path, sizeof(path), "%s/resources/%.*s", dirname(exe_path), (int)name_len, name_start);
    if (pn < 0 || (size_t)pn >= sizeof(path)) return NULL;

    FILE *f = fopen(path, "rb");
    if (!f) return NULL;
    if (fseek(f, 0, SEEK_END) != 0) { fclose(f); return NULL; }
    long sz = ftell(f);
    if (sz < 0) { fclose(f); return NULL; }
    rewind(f);
    char *buf = malloc((size_t)sz + 1);
    if (!buf) { fclose(f); return NULL; }
    if (fread(buf, 1, (size_t)sz, f) != (size_t)sz) { free(buf); fclose(f); return NULL; }
    buf[sz] = '\0';
    fclose(f);
    return buf;
}

/* ── str_hash: sorted frequency signature ── */
static void str_hash(const char *s, int len, char *out) {
    int freq[256] = {0};
    for (int i = 0; i < len; i++) freq[(unsigned char)s[i]]++;
    int counts[256];
    int nc = 0;
    for (int i = 0; i < 256; i++)
        if (freq[i]) counts[nc++] = freq[i];
    /* sort descending */
    for (int i = 0; i < nc - 1; i++)
        for (int j = i + 1; j < nc; j++)
            if (counts[j] > counts[i]) { int t = counts[i]; counts[i] = counts[j]; counts[j] = t; }
    int pos = 0;
    for (int i = 0; i < nc; i++) pos += sprintf(out + pos, "%d", counts[i]);
    out[pos] = '\0';
}

/* ── string list for squares ── */
typedef struct {
    char **data;
    int size, cap;
} StrList;

static void strlist_push(StrList *sl, const char *s) {
    if (sl->size == sl->cap) {
        sl->cap = sl->cap ? sl->cap * 2 : 16;
        sl->data = realloc(sl->data, (size_t)sl->cap * sizeof(char *));
    }
    sl->data[sl->size++] = strdup(s);
}

static void strlist_free(StrList *sl) {
    for (int i = 0; i < sl->size; i++) free(sl->data[i]);
    free(sl->data);
    sl->data = NULL;
    sl->size = sl->cap = 0;
}

static int strlist_contains(const StrList *sl, const char *s) {
    for (int i = 0; i < sl->size; i++)
        if (strcmp(sl->data[i], s) == 0) return 1;
    return 0;
}

static StrList n_digit_squares(int n) {
    StrList sl;
    memset(&sl, 0, sizeof(sl));
    long long lo = (long long)ceil(sqrt(pow(10.0, n - 1)));
    long long hi = (long long)floor(sqrt(pow(10.0, n) - 1));
    char buf[32];
    for (long long i = lo; i <= hi; i++) {
        sprintf(buf, "%lld", i * i);
        strlist_push(&sl, buf);
    }
    return sl;
}

/* ── anagram buckets ── */
#define MAX_WORDS 2200
#define MAX_WORD_LEN 32
#define MAX_BUCKET_WORDS 32

typedef struct {
    char canonical[MAX_WORD_LEN];
    char words[MAX_BUCKET_WORDS][MAX_WORD_LEN];
    int word_count;
    int word_len;
} Bucket;

long long solve(int argc, char *argv[]) {
    if (argc < 2) { fprintf(stderr, "Usage: prog <file_url>\n"); return -1; }

    char *text = get_text_file(argv[1]);
    if (!text) { fprintf(stderr, "Cannot read file\n"); return -1; }

    /* parse words */
    static char word_store[MAX_WORDS][MAX_WORD_LEN];
    int n_words = 0;
    char *p = text;
    while (*p) {
        while (*p == '"' || *p == ',' || *p == ' ' || *p == '\n' || *p == '\r') p++;
        if (*p == '\0') break;
        char *start = p;
        while (*p && *p != '"' && *p != ',') p++;
        int wlen = (int)(p - start);
        if (wlen > 0 && n_words < MAX_WORDS) {
            memcpy(word_store[n_words], start, (size_t)wlen);
            word_store[n_words][wlen] = '\0';
            n_words++;
        }
    }
    free(text);

    /* build buckets */
    static Bucket buckets[MAX_WORDS];
    int n_buckets = 0;

    for (int i = 0; i < n_words; i++) {
        const char *w = word_store[i];
        int wlen = (int)strlen(w);
        char can[MAX_WORD_LEN];
        memcpy(can, w, (size_t)wlen + 1);
        /* insertion sort */
        for (int a = 1; a < wlen; a++) {
            char key = can[a];
            int b = a - 1;
            while (b >= 0 && can[b] > key) { can[b + 1] = can[b]; b--; }
            can[b + 1] = key;
        }
        int found = -1;
        for (int j = 0; j < n_buckets; j++) {
            if (buckets[j].word_len == wlen && strcmp(buckets[j].canonical, can) == 0) {
                found = j;
                break;
            }
        }
        if (found == -1) {
            found = n_buckets++;
            strncpy(buckets[found].canonical, can, MAX_WORD_LEN - 1);
            buckets[found].canonical[MAX_WORD_LEN - 1] = '\0';
            buckets[found].word_count = 0;
            buckets[found].word_len = wlen;
        }
        if (buckets[found].word_count < MAX_BUCKET_WORDS) {
            strncpy(buckets[found].words[buckets[found].word_count], w, MAX_WORD_LEN - 1);
            buckets[found].words[buckets[found].word_count][MAX_WORD_LEN - 1] = '\0';
            buckets[found].word_count++;
        }
    }

    /* collect valid buckets */
    Bucket *valid_buckets[MAX_WORDS];
    int n_valid = 0;
    for (int i = 0; i < n_buckets; i++)
        if (buckets[i].word_count > 1) valid_buckets[n_valid++] = &buckets[i];

    /* unique word lengths, sorted descending */
    int lengths[MAX_WORD_LEN];
    int n_lengths = 0;
    for (int i = 0; i < n_valid; i++) {
        int wl = valid_buckets[i]->word_len;
        int dup = 0;
        for (int j = 0; j < n_lengths; j++)
            if (lengths[j] == wl) { dup = 1; break; }
        if (!dup) lengths[n_lengths++] = wl;
    }
    for (int a = 0; a < n_lengths - 1; a++)
        for (int b = a + 1; b < n_lengths; b++)
            if (lengths[b] > lengths[a]) { int t = lengths[a]; lengths[a] = lengths[b]; lengths[b] = t; }

    long long best = 0;

    for (int li = 0; li < n_lengths && best == 0; li++) {
        int wl = lengths[li];
        StrList squares = n_digit_squares(wl);

        for (int bi = 0; bi < n_valid; bi++) {
            Bucket *bkt = valid_buckets[bi];
            if (bkt->word_len != wl) continue;

            for (int wi = 0; wi < bkt->word_count; wi++) {
                const char *word = bkt->words[wi];
                char word_hash[64];
                str_hash(word, wl, word_hash);

                for (int si = 0; si < squares.size; si++) {
                    const char *sq = squares.data[si];

                    char sq_hash[64];
                    str_hash(sq, wl, sq_hash);
                    if (strcmp(word_hash, sq_hash) != 0) continue;

                    /* build char_map */
                    char char_map_key[MAX_WORD_LEN];
                    char char_map_val[MAX_WORD_LEN];
                    int map_size = 0;
                    int valid = 1;

                    for (int k = 0; k < wl && valid; k++) {
                        char c = word[k];
                        char d = sq[k];
                        int fc = -1;
                        for (int m = 0; m < map_size; m++)
                            if (char_map_key[m] == c) { fc = m; break; }
                        if (fc == -1) {
                            char_map_key[map_size] = c;
                            char_map_val[map_size] = d;
                            map_size++;
                        } else {
                            if (char_map_val[fc] != d) valid = 0;
                        }
                    }
                    if (!valid) continue;

                    /* check unique char count */
                    {
                        char seen[MAX_WORD_LEN];
                        int ns = 0;
                        for (int k = 0; k < wl; k++) {
                            int f = 0;
                            for (int m = 0; m < ns; m++)
                                if (seen[m] == word[k]) { f = 1; break; }
                            if (!f) seen[ns++] = word[k];
                        }
                        if (map_size != ns) valid = 0;
                    }
                    if (!valid) continue;

                    /* injective check */
                    for (int a2 = 0; a2 < map_size && valid; a2++)
                        for (int b2 = a2 + 1; b2 < map_size && valid; b2++)
                            if (char_map_val[a2] == char_map_val[b2]) valid = 0;
                    if (!valid) continue;

                    /* apply to other words */
                    for (int oi = 0; oi < bkt->word_count; oi++) {
                        if (oi == wi) continue;
                        const char *other = bkt->words[oi];
                        char other_num[MAX_WORD_LEN];
                        int ok = 1;
                        for (int k = 0; k < wl && ok; k++) {
                            int fc = -1;
                            for (int m = 0; m < map_size; m++)
                                if (char_map_key[m] == other[k]) { fc = m; break; }
                            if (fc == -1) { ok = 0; break; }
                            other_num[k] = char_map_val[fc];
                        }
                        other_num[wl] = '\0';
                        if (!ok) continue;
                        if (other_num[0] == '0') continue;
                        if (!strlist_contains(&squares, other_num)) continue;
                        long long v1 = atoll(sq);
                        long long v2 = atoll(other_num);
                        long long mx = v1 > v2 ? v1 : v2;
                        if (mx > best) best = mx;
                    }
                }
            }
        }
        strlist_free(&squares);
    }

    return best;
}

int main(int argc, char *argv[]) {
    int runs = 1;

    char **solve_argv = malloc((size_t)argc * sizeof(char *));
    if (!solve_argv) { fprintf(stderr, "runner: out of memory\n"); return 1; }
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