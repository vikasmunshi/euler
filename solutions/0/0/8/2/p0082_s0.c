/* Solution to Euler Problem 82: Path Sum: Three Ways. */
#include <libgen.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define MAX_N 80

static int matrix[MAX_N][MAX_N];
static int n_rows;
static int n_cols;

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

static void parse_matrix(const char *content) {
    n_rows = 0;
    n_cols = 0;
    const char *p = content;
    while (*p) {
        while (*p == '\r' || *p == '\n') p++;
        if (*p == '\0') break;
        int col = 0;
        while (*p && *p != '\n' && *p != '\r') {
            while (*p == ' ' || *p == '\t') p++;
            if (*p == '\0' || *p == '\n' || *p == '\r') break;
            int val = 0;
            while (*p >= '0' && *p <= '9') {
                val = val * 10 + (*p - '0');
                p++;
            }
            matrix[n_rows][col++] = val;
            while (*p == ',' || *p == ' ' || *p == '\t') p++;
        }
        if (col > 0) {
            if (n_rows == 0) n_cols = col;
            n_rows++;
        }
    }
}

static void reduce_column(int col) {
    int new_entries[MAX_N];
    for (int row = 0; row < n_rows; row++) {
        int best = -1;
        for (int target = 0; target < n_rows; target++) {
            int r_min = row < target ? row : target;
            int r_max = row > target ? row : target;
            int range_sum = 0;
            for (int cell = r_min; cell <= r_max; cell++) {
                range_sum += matrix[cell][col - 1];
            }
            int cost = range_sum + matrix[target][col];
            if (best < 0 || cost < best) {
                best = cost;
            }
        }
        new_entries[row] = best;
    }
    for (int row = 0; row < n_rows; row++) {
        matrix[row][col - 1] = new_entries[row];
    }
}

long long solve(int argc, char *argv[]) {
    const char *default_content =
        "131, 673, 234, 103, 18\n"
        "201, 96, 342, 965, 150\n"
        "630, 803, 746, 422, 111\n"
        "537, 699, 497, 121, 956\n"
        "805, 732, 524, 37, 331\n";

    char *content = NULL;
    int free_content = 0;

    if (argc >= 2 && argv[1][0] != '\0') {
        content = get_text_file(argv[1]);
        if (!content) return -1;
        free_content = 1;
    } else {
        content = (char *)default_content;
        free_content = 0;
    }

    parse_matrix(content);
    if (free_content) free(content);

    for (int col = n_cols - 1; col > 0; col--) {
        reduce_column(col);
    }

    int ans = matrix[0][0];
    for (int row = 1; row < n_rows; row++) {
        if (matrix[row][0] < ans) ans = matrix[row][0];
    }

    return (long long)ans;
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