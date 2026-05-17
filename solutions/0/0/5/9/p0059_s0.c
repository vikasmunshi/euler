/* Solution to Euler Problem 59: XOR Decryption. */
#include <libgen.h>
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

long long solve(int argc, char *argv[]) {
    if (argc < 4) return -1;

    const char *file_url    = argv[1];
    int         key_length  = atoi(argv[2]);
    const char *most_common = argv[3];

    char *contents = get_text_file(file_url);
    if (!contents) return -1;

    /* Parse comma-separated integers */
    int capacity = 8192;
    int *encrypted = malloc((size_t)capacity * sizeof(int));
    if (!encrypted) { free(contents); return -1; }
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
                if (!tmp) { free(encrypted); free(contents); return -1; }
                encrypted = tmp;
            }
            encrypted[n++] = val;
        }
        if (*ptr == ',') ptr++;
    }
    free(contents);

    if (n == 0 || key_length <= 0) { free(encrypted); return -1; }

    /* Build interleaved slices */
    int *slice_sizes = calloc((size_t)key_length, sizeof(int));
    if (!slice_sizes) { free(encrypted); return -1; }

    for (int j = 0; j < n; j++) slice_sizes[j % key_length]++;

    int **slices = malloc((size_t)key_length * sizeof(int *));
    if (!slices) { free(slice_sizes); free(encrypted); return -1; }

    for (int i = 0; i < key_length; i++) {
        slices[i] = malloc((size_t)(slice_sizes[i] ? slice_sizes[i] : 1) * sizeof(int));
        if (!slices[i]) {
            for (int k = 0; k < i; k++) free(slices[k]);
            free(slices); free(slice_sizes); free(encrypted); return -1;
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
        return -1;
    }

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

    /* Sum all ASCII values of decrypted text */
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

    return total;
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