/* Solution to Euler Problem 84: Monopoly Odds. */
#include "runner.h"

#define BOARD_SIZE 40
#define STATES (BOARD_SIZE * 3)

static const char *board[BOARD_SIZE] = {
    "GO",   "A1",  "CC1", "A2",   "T1",  "R1",  "B1",  "CH1", "B2",  "B3",
    "JAIL", "C1",  "U1",  "C2",   "C3",  "R2",  "D1",  "CC2", "D2",  "D3",
    "FP",   "E1",  "CH2", "E2",   "E3",  "R3",  "F1",  "F2",  "U2",  "F3",
    "G2J",  "G1",  "G2",  "CC3",  "G3",  "R4",  "CH3", "H1",  "T2",  "H2"
};

static int JAIL;

/* Index of the square whose name matches exactly. */
static int name_index(const char *name) {
    for (int i = 0; i < BOARD_SIZE; i++) {
        if (strcmp(board[i], name) == 0) return i;
    }
    return 0;
}

/* Advance clockwise from `position` to the next square whose name starts with `prefix`. */
static int forward_seek(int position, const char *prefix) {
    int len = (int)strlen(prefix);
    for (int i = 1; i <= BOARD_SIZE; i++) {
        int pos = (position + i) % BOARD_SIZE;
        if (strncmp(board[pos], prefix, len) == 0) return pos;
    }
    return position;
}

/* Distribution over *finishing* squares after stopping on `landing`, written into out[BOARD_SIZE].
   G2J sends to jail; CC/CH draw a card (1/16 each); the Chance "back 3" can land on CC3, so its
   destination is resolved recursively to chain into a Community Chest draw. */
static void resolve(int landing, double out[BOARD_SIZE]) {
    for (int i = 0; i < BOARD_SIZE; i++) out[i] = 0.0;
    const char *name = board[landing];
    if (strcmp(name, "G2J") == 0) {
        out[JAIL] += 1.0;
        return;
    }
    if (strncmp(name, "CC", 2) == 0) {
        /* 2/16 movement cards (Advance to GO, Go to Jail); 14/16 stay. */
        out[0] += 1.0 / 16;
        out[JAIL] += 1.0 / 16;
        out[landing] += 14.0 / 16;
        return;
    }
    if (strncmp(name, "CH", 2) == 0) {
        /* 10/16 movement cards; 6/16 stay. "next R" appears twice (2/16 combined). */
        out[0] += 1.0 / 16;                              /* Advance to GO */
        out[JAIL] += 1.0 / 16;                           /* Go to Jail */
        out[name_index("C1")] += 1.0 / 16;               /* Go to C1 */
        out[name_index("E3")] += 1.0 / 16;               /* Go to E3 */
        out[name_index("H2")] += 1.0 / 16;               /* Go to H2 */
        out[name_index("R1")] += 1.0 / 16;               /* Go to R1 */
        out[forward_seek(landing, "R")] += 1.0 / 16;     /* next Railway */
        out[forward_seek(landing, "R")] += 1.0 / 16;     /* next Railway (again) */
        out[forward_seek(landing, "U")] += 1.0 / 16;     /* next Utility */
        double back[BOARD_SIZE];                          /* Go back 3 squares (may chain via CC3) */
        resolve((landing - 3 + BOARD_SIZE) % BOARD_SIZE, back);
        for (int i = 0; i < BOARD_SIZE; i++) out[i] += back[i] / 16.0;
        out[landing] += 6.0 / 16;
        return;
    }
    out[landing] += 1.0;
}

/* Build the transition matrix over the augmented state square*3 + consecutive_doubles. Tracking the
   doubles count (0/1/2 coming into a turn) lets the third successive double send the player straight
   to jail; any move finishing in jail resets the streak. */
static void build_matrix(int dice_size, double matrix[STATES][STATES]) {
    for (int i = 0; i < STATES; i++)
        for (int j = 0; j < STATES; j++) matrix[i][j] = 0.0;

    double roll_probability = 1.0 / ((double)dice_size * dice_size);
    double fin[BOARD_SIZE];
    for (int position = 0; position < BOARD_SIZE; position++) {
        for (int doubles = 0; doubles < 3; doubles++) {
            int s = position * 3 + doubles;
            for (int first = 1; first <= dice_size; first++) {
                for (int second = 1; second <= dice_size; second++) {
                    if (first == second && doubles == 2) {
                        /* Third consecutive double: go directly to jail, streak resets. */
                        matrix[s][JAIL * 3] += roll_probability;
                        continue;
                    }
                    int next_doubles = (first == second) ? doubles + 1 : 0;
                    int landing = (position + first + second) % BOARD_SIZE;
                    resolve(landing, fin);
                    for (int square = 0; square < BOARD_SIZE; square++) {
                        if (fin[square] == 0.0) continue;
                        int streak = (square == JAIL) ? 0 : next_doubles;
                        matrix[s][square * 3 + streak] += roll_probability * fin[square];
                    }
                }
            }
        }
    }
}

/* Power-iterate the chain to its stationary distribution over the augmented states. */
static void stationary(double matrix[STATES][STATES], double dist[STATES]) {
    for (int i = 0; i < STATES; i++) dist[i] = 1.0 / STATES;
    double nxt[STATES];
    for (int iter = 0; iter < 100000; iter++) {
        for (int j = 0; j < STATES; j++) nxt[j] = 0.0;
        for (int i = 0; i < STATES; i++) {
            double weight = dist[i];
            if (weight == 0.0) continue;
            for (int j = 0; j < STATES; j++) {
                if (matrix[i][j] != 0.0) nxt[j] += weight * matrix[i][j];
            }
        }
        double diff = 0.0;
        for (int j = 0; j < STATES; j++) {
            double d = nxt[j] - dist[j];
            if (d < 0) d = -d;
            if (d > diff) diff = d;
            dist[j] = nxt[j];
        }
        if (diff < 1e-15) break;
    }
}

/* Exact solution via the board's stationary distribution (no simulation, so deterministic): build
   the augmented (square, consecutive doubles) transition matrix, power-iterate to the steady state,
   marginalise to per-square probabilities, and report the three most popular squares as a six-digit
   modal string. */
const char *solve(int argc, char *argv[]) {
    int dice_size = (argc > 1) ? parse_int(argv[1]) : 6;

    JAIL = name_index("JAIL");

    static double matrix[STATES][STATES];
    static double dist[STATES];
    build_matrix(dice_size, matrix);
    stationary(matrix, dist);

    double square_probability[BOARD_SIZE];
    for (int square = 0; square < BOARD_SIZE; square++) {
        square_probability[square] = dist[square * 3] + dist[square * 3 + 1] + dist[square * 3 + 2];
    }

    /* Top-3 by masked linear scans; strict `>` keeps the lowest index on ties. */
    int top[3] = {-1, -1, -1};
    double used[BOARD_SIZE];
    memcpy(used, square_probability, sizeof(square_probability));
    for (int t = 0; t < 3; t++) {
        double best = -1.0;
        int best_idx = 0;
        for (int j = 0; j < BOARD_SIZE; j++) {
            if (used[j] > best) {
                best = used[j];
                best_idx = j;
            }
        }
        top[t] = best_idx;
        used[best_idx] = -1.0;
    }

    char *result = malloc(7);
    if (!result) return NULL;
    snprintf(result, 7, "%02d%02d%02d", top[0], top[1], top[2]);
    return result;
}
