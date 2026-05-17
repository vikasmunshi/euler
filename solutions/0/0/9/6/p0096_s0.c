/* Solution to Euler Problem 96: Su Doku. */
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

typedef struct {
    int row;
    int col;
    int possibilities[9];
    int num_possibilities;
} Cell;

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

static int cell_cmp(const void *a, const void *b) {
    const Cell *ca = (const Cell *)a;
    const Cell *cb = (const Cell *)b;
    return ca->num_possibilities - cb->num_possibilities;
}

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

        Cell *updated = malloc((size_t)remaining_count * sizeof(Cell));
        if (!updated && remaining_count > 0) return 0;
        if (remaining_count > 0)
            memcpy(updated, remaining, (size_t)remaining_count * sizeof(Cell));
        update_possibilities(updated, remaining_count, chosen.row, chosen.col, number);

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

static int solve_sudoku(int g[9][9]) {
    Cell cells[81];
    int num_cells = get_all_empty_cells(g, cells);
    return solve_backtracking(g, cells, num_cells);
}

long long solve(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <file_url>\n", argv[0]);
        return -1;
    }

    char *text = get_text_file(argv[1]);
    if (!text) {
        fprintf(stderr, "Cannot read file: %s\n", argv[1]);
        return -1;
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
    return total;
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