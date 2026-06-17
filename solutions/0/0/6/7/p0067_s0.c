/* Solution to Euler Problem 67: Maximum Path Sum II. */
#include "runner.h"



/* Parse whitespace-separated rows into a triangle; row i holds i+1 integers. */
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

/* Bottom-up DP fold: each cell becomes the best path sum from it to the base; O(n^2). */
static long long max_path_sum_triangle(int **triangle, int rows) {
    /* Deep copy so the reduction does not mutate the caller's triangle. */
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

    /* Merge the last row into the one above by adding the larger child, then drop it. */
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
        free(tri[cur_rows - 1]);  /* free the discarded row as soon as it is merged */
        cur_rows--;
    }

    long long result = tri[0][0];  /* apex now holds the maximum path sum */
    free(tri[0]);
    free(tri);
    return result;
}

/* Maximum top-to-base path sum via bottom-up triangle DP; O(n^2) in the row count. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    if (argc < 2) { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    const char *file_url = argv[1];

    char *text = get_text_file(file_url);
    if (!text) {
        fprintf(stderr, "Failed to read triangle file\n");
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }

    int **triangle = NULL;
    int rows = text2triangle(text, &triangle);
    free(text);

    if (rows == 0 || !triangle) { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }

    long long result = max_path_sum_triangle(triangle, rows);

    for (int i = 0; i < rows; i++) free(triangle[i]);
    free(triangle);

    { snprintf(_answer, sizeof _answer, "%lld", (long long)(result)); return _answer; }
}