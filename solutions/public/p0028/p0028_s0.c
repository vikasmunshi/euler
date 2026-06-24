/* Solution to Euler Problem 28: Number Spiral Diagonals. */
#include "runner.h"

/* Build the spiral by stepping to the nearest free neighbour and sum its diagonals;
   O(size^2) reference check for the closed form. */
static long long number_spiral_with_diagonal_sum(long long size) {
    int half = (int)(size / 2);
    int dim = (int)size;
    int *grid = calloc((size_t)(dim * dim), sizeof(int));
    if (!grid) return -1;

    /* grid[(row+half)*dim + (col+half)] holds the spiral value at (col, row);
       the +half offset maps signed coordinates onto non-negative array indices */
    int x = 0, y = 0;
    grid[half * dim + half] = 1;

    /* right, down, left, up — matching Python's adjacent order */
    static const int dx[] = {1, 0, -1, 0};
    static const int dy[] = {0, -1, 0, 1};

    /* place each value in the unoccupied neighbour nearest the origin (a 0 cell is empty) */
    for (int number = 2; number <= dim * dim; number++) {
        int best_x = 0, best_y = 0, best_dist = dim * dim + 1;
        for (int d = 0; d < 4; d++) {
            int nx = x + dx[d], ny = y + dy[d];
            if (nx < -half || nx > half || ny < -half || ny > half) continue;
            if (grid[(ny + half) * dim + (nx + half)] != 0) continue;
            int dist = nx * nx + ny * ny;
            if (dist < best_dist) {
                best_dist = dist;
                best_x = nx;
                best_y = ny;
            }
        }
        x = best_x;
        y = best_y;
        grid[(y + half) * dim + (x + half)] = number;
    }

    printf("Generated spiral for size %lld with diagonal elements highlighted in\x1b[34m blue\x1b[0m:\n", size);
    for (int row = half; row >= -half; row--) {
        for (int col = -half; col <= half; col++) {
            int val = grid[(row + half) * dim + (col + half)];
            if (col == row || col == -row)
                printf("\x1b[34m%2d\x1b[0m", val);
            else
                printf("%2d", val);
            if (col < half) printf(" ");
        }
        printf("\n");
    }

    long long diagonal_sum = 0;
    for (int row = -half; row <= half; row++)
        for (int col = -half; col <= half; col++)
            if (col == row || col == -row)
                diagonal_sum += grid[(row + half) * dim + (col + half)];

    long long formula_result = (size * (size * (4 * size + 3) + 8) - 9) / 6;
    const char *mark = (formula_result == diagonal_sum)
        ? "\x1b[32m\xe2\x9c\x93" : "\x1b[31m\xe2\x9c\x97";
    printf("%s size=%lld; formula_result=%lld; diagonal_sum=%lld\x1b[0m\n",
           mark, size, formula_result, diagonal_sum);

    free(grid);
    return diagonal_sum;
}

/* Each ring's four diagonal corners form an arithmetic pattern that sums in closed
   form to (N*(N*(4N+3)+8)-9)/6; O(1). The O(size^2) spiral simulation runs only under
   --show for small grids as a cross-check. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    long long size = parse_int(argv[1]);
    if (show && size <= 10)
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(number_spiral_with_diagonal_sum(size))); return _answer; }
    { snprintf(_answer, sizeof _answer, "%lld", (long long)((size * (size * (4 * size + 3) + 8) - 9) / 6)); return _answer; }
}