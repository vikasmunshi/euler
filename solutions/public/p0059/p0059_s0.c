/* Solution to Euler Problem 59: XOR Decryption. */
#include "runner.h"


/*
 * Break a repeating-key XOR cipher whose key is key_length lowercase letters.
 * A key of length k splits the ciphertext into k interleaved slices, each one a
 * single-byte XOR cipher; each slice is solved independently by trying all 26
 * lowercase key bytes and keeping the one whose decryption yields the most
 * common letters. This turns a 26^k search into k linear scans: O(26 * n).
 */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    if (argc < 4) { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }

    const char *file_url    = argv[1];
    int         key_length  = parse_int(argv[2]);
    const char *most_common = argv[3];

    char *contents = get_text_file(file_url);
    if (!contents) { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }

    /* Parse comma-separated integers; grow the array by doubling for amortised O(n) total copying */
    int capacity = 8192;
    int *encrypted = malloc((size_t)capacity * sizeof(int));
    if (!encrypted) { free(contents); { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; } }
    int n = 0;

    char *ptr = contents;
    while (*ptr) {
        while (*ptr == ' ' || *ptr == '\n' || *ptr == '\r' || *ptr == '\t') ptr++;
        if (*ptr == '\0') break;
        int val = 0, got = 0;
        while (*ptr >= '0' && *ptr <= '9') {
            val = val * 10 + (*ptr - '0');
            ptr++;
            got = 1;
        }
        if (got) {
            if (n >= capacity) {
                capacity *= 2;
                int *tmp = realloc(encrypted, (size_t)capacity * sizeof(int));
                if (!tmp) { free(encrypted); free(contents); { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; } }
                encrypted = tmp;
            }
            encrypted[n++] = val;
        }
        if (*ptr == ',') ptr++;
    }
    free(contents);

    if (n == 0 || key_length <= 0) { free(encrypted); { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; } }

    /* Build interleaved slices: slice i holds positions i, i+k, i+2k, ...                       */
    /* Two passes - count each slice's size first, then allocate exactly and route elements in.  */
    int *slice_sizes = calloc((size_t)key_length, sizeof(int));
    if (!slice_sizes) { free(encrypted); { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; } }

    for (int j = 0; j < n; j++) slice_sizes[j % key_length]++;

    int **slices = malloc((size_t)key_length * sizeof(int *));
    if (!slices) { free(slice_sizes); free(encrypted); { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; } }

    for (int i = 0; i < key_length; i++) {
        slices[i] = malloc((size_t)(slice_sizes[i] ? slice_sizes[i] : 1) * sizeof(int));
        if (!slices[i]) {
            for (int k = 0; k < i; k++) free(slices[k]);
            free(slices); free(slice_sizes); free(encrypted); { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
        }
        slice_sizes[i] = 0;
    }
    for (int j = 0; j < n; j++) {
        int i = j % key_length;
        slices[i][slice_sizes[i]++] = encrypted[j];
    }
    free(encrypted);

    int common_len = (int)strlen(most_common);

    int *best_key   = calloc((size_t)key_length, sizeof(int));
    int *best_score = calloc((size_t)key_length, sizeof(int));
    if (!best_key || !best_score) {
        for (int i = 0; i < key_length; i++) free(slices[i]);
        free(slices); free(slice_sizes); free(best_key); free(best_score);
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }

    /* Score every lowercase candidate byte per slice by common-letter count; keep the best */
    for (int kb = 97; kb <= 122; kb++) {
        for (int i = 0; i < key_length; i++) {
            int score = 0;
            int sz = slice_sizes[i];
            for (int j = 0; j < sz; j++) {
                char c = (char)(slices[i][j] ^ kb);
                for (int m = 0; m < common_len; m++) {
                    if (c == most_common[m]) { score++; break; }
                }
            }
            if (score > best_score[i]) {
                best_score[i] = score;
                best_key[i]   = kb;
            }
        }
    }

    /* Decrypt with the recovered per-position key and sum all plaintext ASCII values */
    long long total = 0;
    for (int i = 0; i < key_length; i++) {
        int kb = best_key[i];
        int sz = slice_sizes[i];
        for (int j = 0; j < sz; j++) {
            total += (slices[i][j] ^ kb);
        }
        free(slices[i]);
    }

    free(slices);
    free(slice_sizes);
    free(best_key);
    free(best_score);

    { snprintf(_answer, sizeof _answer, "%lld", (long long)(total)); return _answer; }
}