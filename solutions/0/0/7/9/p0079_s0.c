/* Solution to Euler Problem 79: Passcode Derivation. */
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

#define MAX_DIGITS 10
#define MAX_LINES  200

long long solve(int argc, char *argv[]) {
    if (argc < 3) return -1;
    int asked_characters = atoi(argv[1]);
    const char *file_url = argv[2];

    char *content = get_text_file(file_url);
    if (!content) {
        fprintf(stderr, "Could not open file\n");
        return -1;
    }

    /* Parse and deduplicate lines */
    char lines[MAX_LINES][16];
    int line_count = 0;

    char *p = content;
    while (*p) {
        while (*p == '\r' || *p == '\n' || *p == ' ') p++;
        if (*p == '\0') break;
        int li = 0;
        char token[16];
        while (*p && *p != '\r' && *p != '\n' && li < 15) {
            token[li++] = *p++;
        }
        token[li] = '\0';
        if (li == 0) continue;
        int dup = 0;
        for (int i = 0; i < line_count; i++) {
            if (strcmp(lines[i], token) == 0) { dup = 1; break; }
        }
        if (!dup && line_count < MAX_LINES) {
            strncpy(lines[line_count], token, 15);
            lines[line_count][15] = '\0';
            line_count++;
        }
    }
    free(content);

    /* Collect distinct characters */
    char chars[MAX_DIGITS];
    int num_chars = 0;
    for (int i = 0; i < line_count; i++) {
        for (int j = 0; lines[i][j]; j++) {
            char c = lines[i][j];
            int found = 0;
            for (int k = 0; k < num_chars; k++) {
                if (chars[k] == c) { found = 1; break; }
            }
            if (!found && num_chars < MAX_DIGITS) chars[num_chars++] = c;
        }
    }

    /* Build successor graph using bitmasks */
    unsigned int successor[MAX_DIGITS] = {0};
    int num_pairs = asked_characters - 1;

    for (int i = 0; i < line_count; i++) {
        for (int j = 0; j < num_pairs; j++) {
            if (lines[i][j] == '\0' || lines[i][j + 1] == '\0') break;
            char a = lines[i][j];
            char b = lines[i][j + 1];
            int ai = -1, bi = -1;
            for (int k = 0; k < num_chars; k++) {
                if (chars[k] == a) ai = k;
                if (chars[k] == b) bi = k;
            }
            if (ai >= 0 && bi >= 0) {
                successor[ai] |= (1u << bi);
            }
        }
    }

    /* Reverse topological sort: repeatedly find node with no active successors */
    int active[MAX_DIGITS];
    for (int i = 0; i < num_chars; i++) active[i] = 1;

    char passcode[MAX_DIGITS + 1];
    int passcode_len = 0;
    passcode[0] = '\0';

    int remaining = num_chars;
    while (remaining > 0) {
        /* Build active mask */
        unsigned int active_mask = 0;
        for (int i = 0; i < num_chars; i++) {
            if (active[i]) active_mask |= (1u << i);
        }

        int found = -1;
        for (int i = 0; i < num_chars; i++) {
            if (!active[i]) continue;
            if ((successor[i] & active_mask) == 0) {
                found = i;
                break;
            }
        }
        if (found < 0) {
            fprintf(stderr, "Cycle detected in constraints\n");
            return -1;
        }

        /* Prepend chars[found] to passcode */
        for (int i = passcode_len; i >= 0; i--) {
            passcode[i + 1] = passcode[i];
        }
        passcode[0] = chars[found];
        passcode_len++;

        active[found] = 0;
        remaining--;
    }

    return (long long)atoll(passcode);
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