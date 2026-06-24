/* Solution to Euler Problem 18: Maximum Path Sum I. */
#include "runner.h"

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

/* Collapse the triangle bottom-up, folding each row's larger child upward; return the apex sum; O(N^2). */
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

/* Bottom-up dynamic programming over the triangle's optimal substructure; O(N^2) in the rows. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    if (argc < 2) { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }

    const char *triangle_str_key = argv[1];
    const char *text;
    if (strcmp(triangle_str_key, "TRIANGLE_A") == 0) {
        text = TRIANGLE_A;
    } else if (strcmp(triangle_str_key, "TRIANGLE_B") == 0) {
        text = TRIANGLE_B;
    } else {
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }

    int **triangle = NULL;
    int *row_sizes = NULL;
    int rows = text2triangle(text, &triangle, &row_sizes);
    if (rows < 0) { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }

    long long result = max_path_sum_triangle(triangle, row_sizes, rows);

    for (int i = 0; i < rows; i++) free(triangle[i]);
    free(triangle);
    free(row_sizes);

    { snprintf(_answer, sizeof _answer, "%lld", (long long)(result)); return _answer; }
}
