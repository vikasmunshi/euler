/* Solution to Euler Problem 96: Su Doku. */
#include "runner.h"



/* Backtracking search over empty cells with MRV ordering and forward checking.
   Each empty cell carries its candidate digits; the search branches on the cell
   with fewest candidates and copies the working set so undo is free.
   Worst case exponential in empty-cell count, but near-linear on these puzzles. */
typedef struct {
    int row;
    int col;
    int possibilities[9];
    int num_possibilities;
} Cell;

/* Candidates for one empty cell: {1..9} minus the digits seen in its row, column, and box. */
static void get_possibilities(int g[9][9], int row, int col, int *poss, int *num_poss) {
    int possible[10] = {0,1,1,1,1,1,1,1,1,1};

    for (int c = 0; c < 9; c++) {
        if (g[row][c] != 0) possible[g[row][c]] = 0;
    }
    for (int r = 0; r < 9; r++) {
        if (g[r][col] != 0) possible[g[r][col]] = 0;
    }
    int box_row = row - row % 3;
    int box_col = col - col % 3;
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            int v = g[box_row + i][box_col + j];
            if (v != 0) possible[v] = 0;
        }
    }

    *num_poss = 0;
    for (int d = 1; d <= 9; d++) {
        if (possible[d]) poss[(*num_poss)++] = d;
    }
}

/* Build the working set once: a (row, col, candidates) triple for every empty cell. */
static int get_all_empty_cells(int g[9][9], Cell *cells) {
    int count = 0;
    for (int row = 0; row < 9; row++) {
        for (int col = 0; col < 9; col++) {
            if (g[row][col] == 0) {
                cells[count].row = row;
                cells[count].col = col;
                get_possibilities(g, row, col,
                                  cells[count].possibilities,
                                  &cells[count].num_possibilities);
                count++;
            }
        }
    }
    return count;
}

/* Forward checking: drop the placed digit from every cell sharing its row, column, or box. */
static void update_possibilities(Cell *cells, int num_cells, int row, int col, int number) {
    for (int i = 0; i < num_cells; i++) {
        int r = cells[i].row;
        int c = cells[i].col;
        if (r == row || c == col ||
            (r / 3 == row / 3 && c / 3 == col / 3)) {
            int found = -1;
            for (int k = 0; k < cells[i].num_possibilities; k++) {
                if (cells[i].possibilities[k] == number) {
                    found = k;
                    break;
                }
            }
            if (found >= 0) {
                for (int k = found; k < cells[i].num_possibilities - 1; k++) {
                    cells[i].possibilities[k] = cells[i].possibilities[k + 1];
                }
                cells[i].num_possibilities--;
            }
        }
    }
}

/* Order cells by candidate count, ascending, so qsort surfaces the MRV cell first. */
static int cell_cmp(const void *a, const void *b) {
    const Cell *ca = (const Cell *)a;
    const Cell *cb = (const Cell *)b;
    return ca->num_possibilities - cb->num_possibilities;
}

/* Depth-first backtracking: pick the MRV cell, try each candidate, propagate on a copy. */
static int solve_backtracking(int g[9][9], Cell *cells, int num_cells) {
    if (num_cells == 0) return 1;

    qsort(cells, (size_t)num_cells, sizeof(Cell), cell_cmp);

    Cell chosen = cells[0];

    if (chosen.num_possibilities == 0) return 0;

    Cell *remaining = cells + 1;
    int remaining_count = num_cells - 1;

    for (int pi = 0; pi < chosen.num_possibilities; pi++) {
        int number = chosen.possibilities[pi];
        g[chosen.row][chosen.col] = number;

        /* Copy-before-mutate: editing the copy leaves the caller's set intact for backtracking. */
        Cell *updated = malloc((size_t)remaining_count * sizeof(Cell));
        if (!updated && remaining_count > 0) return 0;
        if (remaining_count > 0)
            memcpy(updated, remaining, (size_t)remaining_count * sizeof(Cell));
        update_possibilities(updated, remaining_count, chosen.row, chosen.col, number);

        /* Fail-fast: a cell drained of candidates means this branch is already doomed. */
        int feasible = 1;
        for (int i = 0; i < remaining_count; i++) {
            if (updated[i].num_possibilities == 0) {
                feasible = 0;
                break;
            }
        }

        if (feasible && solve_backtracking(g, updated, remaining_count)) {
            free(updated);
            return 1;
        }

        free(updated);
        g[chosen.row][chosen.col] = 0;
    }

    return 0;
}

/* Collect the empty cells and run the backtracking search on the grid in place. */
static int solve_sudoku(int g[9][9]) {
    Cell cells[81];
    int num_cells = get_all_empty_cells(g, cells);
    return solve_backtracking(g, cells, num_cells);
}

const char *solve(int argc, char *argv[]) {
    /* Sum each solved grid's top-left 3-digit number across all fifty puzzles. */
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
                if (solve_sudoku(current_grid)) {
                    total += current_grid[0][0] * 100 + current_grid[0][1] * 10 + current_grid[0][2];
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