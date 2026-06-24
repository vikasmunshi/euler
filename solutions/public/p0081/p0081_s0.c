/* Solution to Euler Problem 81: Path Sum: Two Ways. */
#include "runner.h"

#define MAX_SIZE 80
#define MAX_LINE 4096

static int matrix[MAX_SIZE][MAX_SIZE];
static int grid_size;



static const char *default_content =
    "131, 673, 234, 103, 18\n"
    "201, 96, 342, 965, 150\n"
    "630, 803, 746, 422, 111\n"
    "537, 699, 497, 121, 956\n"
    "805, 732, 524, 37, 331\n";

/* Parse the comma-separated grid into matrix[][], recording the side length in grid_size. */
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

/* Emit cell coordinates in reverse anti-diagonal order (bottom-right first), so each cell is
   visited only after its right and lower neighbours - the topological order the DP needs. */
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

        /* Sentinel -1 means "no neighbour yet"; valid since all costs are non-negative. */
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

/* Minimum right/down path sum via in-place DP over the grid: each cell accumulates the smaller
   of its right and lower neighbour's finalised cost; reverse anti-diagonal sweep, O(N^2). */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    const char *content = NULL;
    char *allocated = NULL;

    if (argc >= 2 && argv[1][0] != '\0') {
        allocated = get_text_file(argv[1]);
        if (!allocated) {
            { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
        }
        content = allocated;
    }

    if (!content) {
        content = default_content;
    }

    long long result = path_sum_two_ways(content);
    free(allocated);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(result)); return _answer; }
}