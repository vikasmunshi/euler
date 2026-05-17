/* Solution to Euler Problem 67: Maximum Path Sum II. */
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

static int text2triangle(const char *text, int ***triangle_out) {
    int rows = 0;
    const char *p = text;
    while (*p) {
        while (*p == '\r' || *p == '\n') p++;
        if (*p == '\0') break;
        rows++;
        while (*p && *p != '\r' && *p != '\n') p++;
    }

    int **triangle = malloc((size_t)rows * sizeof(int *));
    if (!triangle) return 0;

    p = text;
    int row = 0;
    while (*p && row < rows) {
        while (*p == '\r' || *p == '\n') p++;
        if (*p == '\0') break;

        int count = row + 1;
        triangle[row] = malloc((size_t)count * sizeof(int));
        if (!triangle[row]) return 0;

        for (int i = 0; i < count; i++) {
            while (*p == ' ') p++;
            triangle[row][i] = atoi(p);
            while (*p && *p != ' ' && *p != '\r' && *p != '\n') p++;
        }
        while (*p && *p != '\r' && *p != '\n') p++;
        row++;
    }

    *triangle_out = triangle;
    return rows;
}

static long long max_path_sum_triangle(int **triangle, int rows) {
    /* Make a deep copy */
    int **tri = malloc((size_t)rows * sizeof(int *));
    if (!tri) return -1;
    for (int i = 0; i < rows; i++) {
        tri[i] = malloc((size_t)(i + 1) * sizeof(int));
        if (!tri[i]) {
            for (int j = 0; j < i; j++) free(tri[j]);
            free(tri);
            return -1;
        }
        memcpy(tri[i], triangle[i], (size_t)(i + 1) * sizeof(int));
    }

    int cur_rows = rows;
    while (cur_rows > 1) {
        int *bottom = tri[cur_rows - 1];
        int *second = tri[cur_rows - 2];
        int second_len = cur_rows - 1;
        for (int i = 0; i < second_len; i++) {
            int left = bottom[i];
            int right = bottom[i + 1];
            second[i] = second[i] + (left > right ? left : right);
        }
        free(tri[cur_rows - 1]);
        cur_rows--;
    }

    long long result = tri[0][0];
    free(tri[0]);
    free(tri);
    return result;
}

long long solve(int argc, char *argv[]) {
    if (argc < 2) return -1;
    const char *file_url = argv[1];

    char *text = get_text_file(file_url);
    if (!text) {
        fprintf(stderr, "Failed to read triangle file\n");
        return -1;
    }

    int **triangle = NULL;
    int rows = text2triangle(text, &triangle);
    free(text);

    if (rows == 0 || !triangle) return -1;

    long long result = max_path_sum_triangle(triangle, rows);

    for (int i = 0; i < rows; i++) free(triangle[i]);
    free(triangle);

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