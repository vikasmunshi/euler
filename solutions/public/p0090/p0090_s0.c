/* Solution to Euler Problem 90: Cube Digit Pairs. */
#include "runner.h"

/* True if the cube shows the digit, treating 6 and 9 as interchangeable via the flip rule. */
static int can_display(int *cube, int digit) {
    for (int i = 0; i < 6; i++) {
        if (cube[i] == digit) return 1;
    }
    if (digit == 6 || digit == 9) {
        for (int i = 0; i < 6; i++) {
            if (cube[i] == 6 || cube[i] == 9) return 1;
        }
    }
    return 0;
}

/* True if every square's two digits can be shown, with either cube supplying the tens digit. */
static int can_pair_display_all(int *cube1, int *cube2) {
    /* squares: 01,04,09,16,25,36,49,64,81 */
    int squares[9][2] = {
        {0,1},{0,4},{0,9},{1,6},{2,5},{3,6},{4,9},{6,4},{8,1}
    };
    for (int s = 0; s < 9; s++) {
        int a = squares[s][0];
        int b = squares[s][1];
        if (!((can_display(cube1, a) && can_display(cube2, b)) ||
              (can_display(cube1, b) && can_display(cube2, a)))) {
            return 0;
        }
    }
    return 1;
}

/* Brute-force over all unordered pairs of the C(10,6)=210 six-digit cubes; O(210^2 * 9). */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    /* Generate all C(10,6) = 210 combinations via six strictly increasing nested indices. */
    int all_cubes[210][6];
    int cube_count = 0;

    for (int a = 0; a <= 4; a++)
    for (int b = a+1; b <= 5; b++)
    for (int c = b+1; c <= 6; c++)
    for (int d = c+1; d <= 7; d++)
    for (int e = d+1; e <= 8; e++)
    for (int f = e+1; f <= 9; f++) {
        all_cubes[cube_count][0] = a;
        all_cubes[cube_count][1] = b;
        all_cubes[cube_count][2] = c;
        all_cubes[cube_count][3] = d;
        all_cubes[cube_count][4] = e;
        all_cubes[cube_count][5] = f;
        cube_count++;
    }

    long long valid_arrangements = 0;
    /* Triangular iteration (j from i) counts each unordered pair once and admits self-pairs. */
    for (int i = 0; i < cube_count; i++) {
        for (int j = i; j < cube_count; j++) {
            if (can_pair_display_all(all_cubes[i], all_cubes[j])) {
                valid_arrangements++;
            }
        }
    }
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(valid_arrangements)); return _answer; }
}