/* Solution to Euler Problem 18: Maximum Path Sum I. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static const char *TRIANGLE_A =
    "3\n"
    "7 4\n"
    "2 4 6\n"
    "8 5 9 3\n";

static const char *TRIANGLE_B =
    "75\n"
    "95 64\n"
    "17 47 82\n"
    "18 35 87 10\n"
    "20 04 82 47 65\n"
    "19 01 23 75 03 34\n"
    "88 02 77 73 07 63 67\n"
    "99 65 04 28 06 16 70 92\n"
    "41 41 26 56 83 40 80 70 33\n"
    "41 48 72 33 47 32 37 16 94 29\n"
    "53 71 44 65 25 43 91 52 97 51 14\n"
    "70 11 33 28 77 73 17 78 39 68 17 57\n"
    "91 71 52 38 17 14 91 43 58 50 27 29 48\n"
    "63 66 04 68 89 53 67 30 73 16 69 87 40 31\n"
    "04 62 98 27 23 09 70 98 73 93 38 53 60 04 23\n";

/* Parse triangle text into a 2D array. Returns number of rows.
 * triangle[i] is a malloc'd array of ints for row i.
 * row_sizes[i] holds the number of elements in row i. */
static int text2triangle(const char *text, int ***triangle_out, int **row_sizes_out) {
    /* Count rows */
    int rows = 0;
    const char *p = text;
    while (*p) {
        if (*p == '\n') rows++;
        p++;
    }

    int **triangle = malloc((size_t)rows * sizeof(int *));
    int *row_sizes = malloc((size_t)rows * sizeof(int));
    if (!triangle || !row_sizes) {
        free(triangle);
        free(row_sizes);
        return -1;
    }

    /* Make a mutable copy of text */
    size_t len = strlen(text);
    char *buf = malloc(len + 1);
    if (!buf) {
        free(triangle);
        free(row_sizes);
        return -1;
    }
    memcpy(buf, text, len + 1);

    int row = 0;
    char *line = buf;
    char *next_line;
    while (row < rows) {
        /* Find end of line */
        next_line = strchr(line, '\n');
        if (next_line) *next_line = '\0';

        /* Count tokens in this line */
        int count = 0;
        char *tmp = strdup(line);
        char *tok = strtok(tmp, " ");
        while (tok) { count++; tok = strtok(NULL, " "); }
        free(tmp);

        triangle[row] = malloc((size_t)count * sizeof(int));
        row_sizes[row] = count;

        int idx = 0;
        char *line2 = strdup(line);
        tok = strtok(line2, " ");
        while (tok) {
            triangle[row][idx++] = atoi(tok);
            tok = strtok(NULL, " ");
        }
        free(line2);

        if (next_line) line = next_line + 1;
        row++;
    }

    free(buf);
    *triangle_out = triangle;
    *row_sizes_out = row_sizes;
    return rows;
}

static long long max_path_sum_triangle(int **triangle, int *row_sizes, int rows) {
    /* Bottom-up DP: collapse last row into second-to-last */
    int current_rows = rows;
    while (current_rows > 1) {
        int *prev = triangle[current_rows - 1];
        int *cur  = triangle[current_rows - 2];
        int cur_size = row_sizes[current_rows - 2];
        for (int i = 0; i < cur_size; i++) {
            int left  = prev[i];
            int right = prev[i + 1];
            cur[i] += (left > right) ? left : right;
        }
        current_rows--;
    }
    return (long long)triangle[0][0];
}

long long solve(int argc, char *argv[]) {
    if (argc < 2) return -1;

    const char *triangle_str_key = argv[1];
    const char *text;
    if (strcmp(triangle_str_key, "TRIANGLE_A") == 0) {
        text = TRIANGLE_A;
    } else if (strcmp(triangle_str_key, "TRIANGLE_B") == 0) {
        text = TRIANGLE_B;
    } else {
        return -1;
    }

    int **triangle = NULL;
    int *row_sizes = NULL;
    int rows = text2triangle(text, &triangle, &row_sizes);
    if (rows < 0) return -1;

    long long result = max_path_sum_triangle(triangle, row_sizes, rows);

    for (int i = 0; i < rows; i++) free(triangle[i]);
    free(triangle);
    free(row_sizes);

    return result;
}

/* Usage: ./file <kwarg>... [--runs=1] [--show]
 * Output: "<runs> <avg_seconds> <result>" */
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