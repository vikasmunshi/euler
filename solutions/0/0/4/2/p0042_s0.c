/* Solution to Euler Problem 42: Coded Triangle Numbers. */
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

static int is_triangle_number(int n) {
    double sq = sqrt((double)(8 * n + 1));
    long long sq_int = (long long)round(sq);
    return (sq_int * sq_int == (long long)(8 * n + 1));
}

static int word_to_num(const char *word) {
    int sum = 0;
    for (const char *c = word; *c != '\0'; c++) {
        if (*c >= 'A' && *c <= 'Z') {
            sum += (*c - 'A' + 1);
        } else if (*c >= 'a' && *c <= 'z') {
            sum += (*c - 'a' + 1);
        }
    }
    return sum;
}

long long solve(int argc, char *argv[]) {
    if (argc < 2) return -1;
    const char *file_url = argv[1];

    char *text = get_text_file(file_url);
    if (!text) return -1;

    long long count = 0;

    char *saveptr = NULL;
    char *token = strtok_r(text, ",", &saveptr);
    while (token != NULL) {
        char word[256];
        int wi = 0;
        for (int i = 0; token[i] != '\0' && wi < 255; i++) {
            char ch = token[i];
            if (ch == '"' || ch == '\r' || ch == '\n' || ch == ' ') continue;
            word[wi++] = ch;
        }
        word[wi] = '\0';

        if (wi > 0) {
            int score = word_to_num(word);
            if (is_triangle_number(score)) {
                count++;
            }
        }

        token = strtok_r(NULL, ",", &saveptr);
    }

    free(text);
    return count;
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