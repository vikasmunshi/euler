/* Solution to Euler Problem 82: Path Sum: Three Ways. */
#include "runner.h"

#define MAX_N 80

static int matrix[MAX_N][MAX_N];
static int n_rows;
static int n_cols;



/* Parse a comma/whitespace-separated integer grid into matrix, n_rows, n_cols. */
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

/* Fold solved column col into col-1: each entry becomes the min cost to reach the
   right edge, where a vertical detour within col-1 is just a range sum of its cells. */
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
    /* Commit only after computing every entry, since each reads other rows of col-1. */
    for (int row = 0; row < n_rows; row++) {
        matrix[row][col - 1] = new_entries[row];
    }
}

/* Column-reduction DP: sweeping columns right to left, collapse the up/down/right
   path into per-column 1-D range-sum minimisations; O(n^3) for an n x n grid. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
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
        if (!content) { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
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

    { snprintf(_answer, sizeof _answer, "%lld", (long long)((long long)ans)); return _answer; }
}