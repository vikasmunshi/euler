/* Solution to Euler Problem 99: Largest Exponential. */
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

long long solve(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <file_url>\n", argv[0]);
        return -1;
    }

    char *content = get_text_file(argv[1]);
    if (!content) {
        fprintf(stderr, "Error: could not load file\n");
        return -1;
    }

    int max_i = 0;
    double max_val = 0.0;
    int line_num = 0;

    char *saveptr = NULL;
    char *line = strtok_r(content, "\n", &saveptr);
    while (line != NULL) {
        /* Strip carriage return if present */
        size_t len = strlen(line);
        if (len > 0 && line[len - 1] == '\r') {
            line[len - 1] = '\0';
            len--;
        }

        if (len == 0) {
            line = strtok_r(NULL, "\n", &saveptr);
            continue;
        }

        line_num++;

        char *comma = strchr(line, ',');
        if (!comma) {
            fprintf(stderr, "Warning: Could not parse line %d: '%s'\n", line_num, line);
            line = strtok_r(NULL, "\n", &saveptr);
            continue;
        }

        *comma = '\0';
        long long base = atoll(line);
        long long exponent = atoll(comma + 1);

        if (base <= 0 || exponent <= 0) {
            fprintf(stderr, "Warning: Skipping invalid values at line %d: base=%lld, exponent=%lld\n",
                    line_num, base, exponent);
            line = strtok_r(NULL, "\n", &saveptr);
            continue;
        }

        double log_val = (double)exponent * log((double)base);
        if (log_val > max_val) {
            max_val = log_val;
            max_i = line_num;
        }

        line = strtok_r(NULL, "\n", &saveptr);
    }

    free(content);
    return (long long)max_i;
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