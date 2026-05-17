/* Solution to Euler Problem 81: Path Sum: Two Ways. */
#include <libgen.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define MAX_SIZE 80
#define MAX_LINE 4096

static int matrix[MAX_SIZE][MAX_SIZE];
static int grid_size;

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

static const char *default_content =
    "131, 673, 234, 103, 18\n"
    "201, 96, 342, 965, 150\n"
    "630, 803, 746, 422, 111\n"
    "537, 699, 497, 121, 956\n"
    "805, 732, 524, 37, 331\n";

static void parse_matrix(const char *content) {
    grid_size = 0;
    const char *p = content;
    char line[MAX_LINE];

    while (*p) {
        const char *end = strchr(p, '\n');
        size_t len;
        if (end) {
            len = (size_t)(end - p);
        } else {
            len = strlen(p);
        }
        if (len == 0) {
            p = end ? end + 1 : p + len;
            if (!end) break;
            continue;
        }
        if (len >= MAX_LINE) len = MAX_LINE - 1;
        memcpy(line, p, len);
        line[len] = '\0';

        int col = 0;
        char *tok = strtok(line, ",");
        while (tok) {
            while (*tok == ' ' || *tok == '\r') tok++;
            matrix[grid_size][col++] = atoi(tok);
            tok = strtok(NULL, ",");
        }
        if (col > 0) {
            grid_size++;
        }
        p = end ? end + 1 : p + len;
        if (!end) break;
    }
}

static void move_diagonally_all(int sz, int *rows, int *cols, int *count) {
    int row = sz - 1, col = sz - 1;
    int n = 0;

    while (row >= 0) {
        rows[n] = row;
        cols[n] = col;
        n++;

        row--;
        col++;

        if (row < 0) {
            row = col - 2;
            col = 0;
        }
        if (col >= sz) {
            int tmp = row;
            row = sz - 1;
            col = tmp;
        }
    }
    *count = n;
}

static long long path_sum_two_ways(const char *content) {
    parse_matrix(content);

    int sz = grid_size;
    int total_cells = sz * sz;
    int *rows = malloc((size_t)total_cells * sizeof(int));
    int *cols = malloc((size_t)total_cells * sizeof(int));
    if (!rows || !cols) {
        free(rows); free(cols);
        return -1;
    }

    int count = 0;
    move_diagonally_all(sz, rows, cols, &count);

    for (int i = 0; i < count; i++) {
        int r = rows[i];
        int c = cols[i];

        int min_neighbor = -1;
        if (r < sz - 1) {
            int v = matrix[r + 1][c];
            if (min_neighbor < 0 || v < min_neighbor) min_neighbor = v;
        }
        if (c < sz - 1) {
            int v = matrix[r][c + 1];
            if (min_neighbor < 0 || v < min_neighbor) min_neighbor = v;
        }
        if (min_neighbor >= 0) {
            matrix[r][c] += min_neighbor;
        }
    }

    long long result = matrix[0][0];
    free(rows);
    free(cols);
    return result;
}

long long solve(int argc, char *argv[]) {
    const char *content = NULL;
    char *allocated = NULL;

    if (argc >= 2 && argv[1][0] != '\0') {
        allocated = get_text_file(argv[1]);
        if (!allocated) {
            return -1;
        }
        content = allocated;
    }

    if (!content) {
        content = default_content;
    }

    long long result = path_sum_two_ways(content);
    free(allocated);
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