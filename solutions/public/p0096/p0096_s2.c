/* Solution to Euler Problem 96: Su Doku. */
#include "runner.h"



/* Constraint propagation (naked + hidden singles) plus depth-first search, after Norvig.
   Each cell's candidate digits are a 9-bit mask: bit (d-1) set => digit d is still possible.
   Deductions run to a fixpoint after every assignment, so most puzzles fall without a guess. */
#define ALL_DIGITS 0x1FF

/* For every cell: its three units (row, column, box) and its 20 peers. */
static int units[81][3][9];
static int peers[81][20];

/* Precompute each cell's row/column/box units and its de-duplicated set of 20 peers. */
static void build_units_peers(void) {
    for (int cell = 0; cell < 81; cell++) {
        int row = cell / 9, col = cell % 9;
        for (int k = 0; k < 9; k++) units[cell][0][k] = row * 9 + k;        /* row unit */
        for (int k = 0; k < 9; k++) units[cell][1][k] = k * 9 + col;        /* column unit */
        int box_row = (row / 3) * 3, box_col = (col / 3) * 3;
        int n = 0;
        for (int i = 0; i < 3; i++)
            for (int j = 0; j < 3; j++)
                units[cell][2][n++] = (box_row + i) * 9 + (box_col + j);    /* box unit */
        int pn = 0;  /* peers = union of the three units minus the cell, de-duplicated */
        for (int u = 0; u < 3; u++) {
            for (int k = 0; k < 9; k++) {
                int pc = units[cell][u][k];
                if (pc == cell) continue;
                int dup = 0;
                for (int q = 0; q < pn; q++) if (peers[cell][q] == pc) { dup = 1; break; }
                if (!dup) peers[cell][pn++] = pc;
            }
        }
    }
}

static int assign(int *values, int cell, int digit);

/* Remove digit from a cell, then propagate naked/hidden singles. Return 0 on a contradiction. */
static int eliminate(int *values, int cell, int digit) {
    int bit = 1 << (digit - 1);
    if (!(values[cell] & bit)) return 1;  /* already eliminated */
    values[cell] &= ~bit;
    int remaining = values[cell];
    if (remaining == 0) return 0;         /* nothing left - contradiction */
    if (__builtin_popcount(remaining) == 1) {
        /* Naked single: cell forced to one digit => strip it from every peer. */
        int only = __builtin_ctz(remaining) + 1;
        for (int p = 0; p < 20; p++)
            if (!eliminate(values, peers[cell][p], only)) return 0;
    }
    for (int u = 0; u < 3; u++) {
        /* Hidden single: if digit fits only one place in this unit, place it there. */
        int place = -1, count = 0;
        for (int k = 0; k < 9; k++) {
            int c = units[cell][u][k];
            if (values[c] & bit) { place = c; count++; }
        }
        if (count == 0) return 0;
        if (count == 1) { if (!assign(values, place, digit)) return 0; }
    }
    return 1;
}

/* Fix a cell to digit by eliminating every other candidate (which propagates). */
static int assign(int *values, int cell, int digit) {
    int others = values[cell] & ~(1 << (digit - 1));
    for (int d = 1; d <= 9; d++)
        if (others & (1 << (d - 1)))
            if (!eliminate(values, cell, d)) return 0;
    return 1;
}

/* Depth-first guess on the unsolved cell with fewest candidates; propagate each guess. */
static int search(int *values) {
    int cell = -1, best = 10;
    for (int c = 0; c < 81; c++) {
        int count = __builtin_popcount(values[c]);
        if (count > 1 && count < best) { best = count; cell = c; }
    }
    if (cell == -1) return 1;  /* every cell down to one candidate - solved */
    int mask = values[cell];
    for (int d = 1; d <= 9; d++) {
        if (mask & (1 << (d - 1))) {
            int trial[81];
            memcpy(trial, values, sizeof(trial));
            if (assign(trial, cell, d) && search(trial)) {
                memcpy(values, trial, sizeof(trial));
                return 1;
            }
        }
    }
    return 0;
}

/* Seed the clues, propagate, search if needed, and return the top-left 3-digit number. */
static int solve_one_grid(int g[9][9]) {
    int values[81];
    for (int i = 0; i < 81; i++) values[i] = ALL_DIGITS;
    for (int r = 0; r < 9; r++)
        for (int c = 0; c < 9; c++) {
            int clue = g[r][c];
            if (clue && !assign(values, r * 9 + c, clue)) return -1;
        }
    if (!search(values)) return -1;
    int d0 = __builtin_ctz(values[0]) + 1;
    int d1 = __builtin_ctz(values[1]) + 1;
    int d2 = __builtin_ctz(values[2]) + 1;
    return d0 * 100 + d1 * 10 + d2;
}

const char *solve(int argc, char *argv[]) {
    /* Solve each grid by constraint propagation to a fixpoint plus depth-first search
       (after Norvig), and sum the top-left 3-digit numbers across all fifty puzzles. */
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

    build_units_peers();

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