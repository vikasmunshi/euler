/* Solution to Euler Problem 96: Su Doku. */
#include "runner.h"



/* Knuth's Algorithm X over a Dancing Links mesh. Sudoku is encoded as an exact-cover
   instance with 324 constraint columns (81 cell, 81 row-digit, 81 col-digit, 81 box-digit)
   and one matrix row per legal (row, col, digit) placement covering exactly those 4.
   Worst case exponential, but covering the smallest column keeps fan-out near one. */
#define NUM_COLUMNS 324
#define MAX_NODES (NUM_COLUMNS + 1 + 9 * 81 * 4)

/* Parallel node arrays - the natural shape for cover/uncover pointer surgery. */
typedef struct {
    int left[MAX_NODES];
    int right[MAX_NODES];
    int up[MAX_NODES];
    int down[MAX_NODES];
    int column[MAX_NODES];  /* column header of each node */
    int size[MAX_NODES];    /* live node count per column header */
    int row_id[MAX_NODES];  /* encodes (row, col, digit) of a node */
    int node_count;
} DLX;

/* Initialise the header ring: id 0 is the root, ids 1..num_columns are the columns. */
static void dlx_init(DLX *d, int num_columns) {
    /* Headers occupy ids 0..num_columns; id 0 is the root, 1..num_columns columns. */
    for (int c = 0; c <= num_columns; c++) {
        d->left[c] = c - 1;
        d->right[c] = c + 1;
        d->up[c] = c;
        d->down[c] = c;
        d->column[c] = c;
        d->size[c] = 0;
    }
    d->left[0] = num_columns;
    d->right[num_columns] = 0;
    d->node_count = num_columns + 1;
}

/* Splice one matrix row (4 nodes) into its column lists, linked in a ring. */
static void dlx_add_row(DLX *d, int row_id, const int cols[4]) {
    int first = -1, prev = -1;
    for (int k = 0; k < 4; k++) {
        int col = cols[k];
        int node = d->node_count++;
        d->row_id[node] = row_id;
        d->column[node] = col;
        /* Insert above the header (at the bottom of the column ring). */
        d->down[node] = col;
        d->up[node] = d->up[col];
        d->down[d->up[col]] = node;
        d->up[col] = node;
        d->size[col]++;
        if (first == -1) {
            first = node;
            d->left[node] = node;
            d->right[node] = node;
        } else {
            d->right[node] = first;
            d->left[node] = prev;
            d->right[prev] = node;
            d->left[first] = node;
        }
        prev = node;
    }
}

/* Cover a column: unlink its header and every row intersecting it from the mesh. */
static void dlx_cover(DLX *d, int col) {
    d->right[d->left[col]] = d->right[col];
    d->left[d->right[col]] = d->left[col];
    for (int i = d->down[col]; i != col; i = d->down[i]) {
        for (int j = d->right[i]; j != i; j = d->right[j]) {
            d->down[d->up[j]] = d->down[j];
            d->up[d->down[j]] = d->up[j];
            d->size[d->column[j]]--;
        }
    }
}

/* Uncover a column: relink it and its rows, exactly reversing dlx_cover. */
static void dlx_uncover(DLX *d, int col) {
    for (int i = d->up[col]; i != col; i = d->up[i]) {
        for (int j = d->left[i]; j != i; j = d->left[j]) {
            d->size[d->column[j]]++;
            d->down[d->up[j]] = j;
            d->up[d->down[j]] = j;
        }
    }
    d->right[d->left[col]] = col;
    d->left[d->right[col]] = col;
}

/* Recurse, always covering the column with fewest options (the S heuristic). */
static int dlx_search(DLX *d, int *solution, int *sol_len) {
    if (d->right[0] == 0) return 1;
    int col = d->right[0];
    int best = d->size[col];
    for (int c = d->right[0]; c != 0; c = d->right[c]) {
        if (d->size[c] < best) { best = d->size[c]; col = c; }
    }
    dlx_cover(d, col);
    for (int r = d->down[col]; r != col; r = d->down[r]) {
        solution[(*sol_len)++] = r;
        for (int j = d->right[r]; j != r; j = d->right[j]) dlx_cover(d, d->column[j]);
        if (dlx_search(d, solution, sol_len)) return 1;
        (*sol_len)--;
        for (int j = d->left[r]; j != r; j = d->left[j]) dlx_uncover(d, d->column[j]);
    }
    dlx_uncover(d, col);
    return 0;
}

/* Build the exact-cover matrix for one grid, solve it, and read off the top-left number. */
static int solve_one_grid(int g[9][9]) {
    static DLX d;
    dlx_init(&d, NUM_COLUMNS);
    for (int row = 0; row < 9; row++) {
        for (int col = 0; col < 9; col++) {
            int clue = g[row][col];
            int box = (row / 3) * 3 + col / 3;
            int dlo = clue ? clue : 1;
            int dhi = clue ? clue : 9;
            for (int digit = dlo; digit <= dhi; digit++) {
                /* Column ids are 1-based; the four covered constraints for (row,col,digit). */
                int cols[4] = {
                    1 + row * 9 + col,
                    1 + 81 + row * 9 + (digit - 1),
                    1 + 162 + col * 9 + (digit - 1),
                    1 + 243 + box * 9 + (digit - 1),
                };
                dlx_add_row(&d, (row * 9 + col) * 9 + (digit - 1), cols);
            }
        }
    }
    int solution[81];
    int sol_len = 0;
    if (!dlx_search(&d, solution, &sol_len)) return -1;
    for (int i = 0; i < sol_len; i++) {
        int rid = d.row_id[solution[i]];
        int r = rid / 81, c = (rid / 9) % 9, dd = rid % 9 + 1;
        g[r][c] = dd;
    }
    return g[0][0] * 100 + g[0][1] * 10 + g[0][2];
}

const char *solve(int argc, char *argv[]) {
    /* Reduce each grid to exact cover, solve with Algorithm X / Dancing Links, and sum
       the top-left 3-digit numbers across all fifty puzzles. */
    static char _answer[32];
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <file_url>\n", argv[0]);
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }

    char *text = get_text_file(argv[1]);
    if (!text) {
        fprintf(stderr, "Cannot read file: %s\n", argv[1]);
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }

    long long total = 0;
    int current_grid[9][9];
    int grid_row = 0;
    int in_grid = 0;

    char *saveptr = NULL;
    char *line = strtok_r(text, "\n", &saveptr);
    while (line) {
        /* Strip trailing \r and spaces */
        int slen = (int)strlen(line);
        while (slen > 0 && (line[slen - 1] == '\r' || line[slen - 1] == ' '))
            line[--slen] = '\0';

        if (strncmp(line, "Grid", 4) == 0) {
            in_grid = 1;
            grid_row = 0;
        } else if (in_grid && slen == 9) {
            for (int c = 0; c < 9; c++) {
                current_grid[grid_row][c] = line[c] - '0';
            }
            grid_row++;
            if (grid_row == 9) {
                int corner = solve_one_grid(current_grid);
                if (corner >= 0) {
                    total += corner;
                } else {
                    fprintf(stderr, "Failed to solve a grid!\n");
                }
                in_grid = 0;
                grid_row = 0;
            }
        }

        line = strtok_r(NULL, "\n", &saveptr);
    }

    free(text);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(total)); return _answer; }
}