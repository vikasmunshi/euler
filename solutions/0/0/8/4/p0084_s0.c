/* Solution to Euler Problem 84: Monopoly Odds. */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

#define BOARD_SIZE 40

static const char *board[BOARD_SIZE] = {
    "GO",   "A1",  "CC1", "A2",   "T1",  "R1",  "B1",  "CH1", "B2",  "B3",
    "JAIL", "C1",  "U1",  "C2",   "C3",  "R2",  "D1",  "CC2", "D2",  "D3",
    "FP",   "E1",  "CH2", "E2",   "E3",  "R3",  "F1",  "F2",  "U2",  "F3",
    "G2J",  "G1",  "G2",  "CC3",  "G3",  "R4",  "CH3", "H1",  "T2",  "H2"
};

/* Find JAIL index */
static int jail_index(void) {
    for (int i = 0; i < BOARD_SIZE; i++) {
        if (strcmp(board[i], "JAIL") == 0) return i;
    }
    return 10; /* default */
}

/* Forward movement: find next square whose name starts with prefix */
static int forward_seek(int position, const char *prefix) {
    int len = (int)strlen(prefix);
    for (int i = 1; i <= BOARD_SIZE; i++) {
        int pos = (position + i) % BOARD_SIZE;
        if (strncmp(board[pos], prefix, len) == 0) return pos;
    }
    return position;
}

/* Backward movement: go back 3 squares */
static int backward_seek(int position) {
    return (position - 3 + BOARD_SIZE) % BOARD_SIZE;
}

/* Card type constants */
#define CARD_NULL       0
#define CARD_FORWARD    1
#define CARD_BACKWARD   2

typedef struct {
    int type;
    char prefix[8];
} Card;

/* Community chest deck */
static Card cc_deck[16];
static int  cc_order[16];
static int  cc_pos;

/* Chance deck */
static Card ch_deck[16];
static int  ch_order[16];
static int  ch_pos;

/* Fisher-Yates shuffle for int array */
static void shuffle_ints(int *arr, int n) {
    for (int i = n - 1; i > 0; i--) {
        int j = rand() % (i + 1);
        int tmp = arr[i]; arr[i] = arr[j]; arr[j] = tmp;
    }
}

static void init_decks(void) {
    /* Community chest: 2 movement cards + 14 null */
    cc_deck[0].type = CARD_FORWARD; strcpy(cc_deck[0].prefix, "GO");
    cc_deck[1].type = CARD_FORWARD; strcpy(cc_deck[1].prefix, "JAIL");
    for (int i = 2; i < 16; i++) { cc_deck[i].type = CARD_NULL; cc_deck[i].prefix[0] = '\0'; }
    for (int i = 0; i < 16; i++) cc_order[i] = i;
    shuffle_ints(cc_order, 16);
    cc_pos = 0;

    /* Chance: 10 movement cards + 6 null */
    ch_deck[0].type = CARD_FORWARD;  strcpy(ch_deck[0].prefix, "GO");
    ch_deck[1].type = CARD_FORWARD;  strcpy(ch_deck[1].prefix, "JAIL");
    ch_deck[2].type = CARD_FORWARD;  strcpy(ch_deck[2].prefix, "C1");
    ch_deck[3].type = CARD_FORWARD;  strcpy(ch_deck[3].prefix, "E3");
    ch_deck[4].type = CARD_FORWARD;  strcpy(ch_deck[4].prefix, "H2");
    ch_deck[5].type = CARD_FORWARD;  strcpy(ch_deck[5].prefix, "R1");
    ch_deck[6].type = CARD_FORWARD;  strcpy(ch_deck[6].prefix, "R");
    ch_deck[7].type = CARD_FORWARD;  strcpy(ch_deck[7].prefix, "R");
    ch_deck[8].type = CARD_FORWARD;  strcpy(ch_deck[8].prefix, "U");
    ch_deck[9].type = CARD_BACKWARD; ch_deck[9].prefix[0] = '\0';
    for (int i = 10; i < 16; i++) { ch_deck[i].type = CARD_NULL; ch_deck[i].prefix[0] = '\0'; }
    for (int i = 0; i < 16; i++) ch_order[i] = i;
    shuffle_ints(ch_order, 16);
    ch_pos = 0;
}

static int next_cc_card(int position) {
    Card *c = &cc_deck[cc_order[cc_pos]];
    cc_pos = (cc_pos + 1) % 16;
    if (c->type == CARD_FORWARD) {
        /* Absolute forward: find that square starting from position=0 effectively */
        /* We need the exact square; use forward_seek from position-1 so we scan full board */
        /* Actually, "Advance to GO/JAIL" means go directly there. Use forward_seek from current pos. */
        return forward_seek(position - 1 + BOARD_SIZE, c->prefix);
    }
    return position;
}

static int next_ch_card(int position) {
    Card *c = &ch_deck[ch_order[ch_pos]];
    ch_pos = (ch_pos + 1) % 16;
    if (c->type == CARD_FORWARD) {
        if (strcmp(c->prefix, "GO") == 0 || strcmp(c->prefix, "JAIL") == 0 ||
            strcmp(c->prefix, "C1") == 0 || strcmp(c->prefix, "E3") == 0  ||
            strcmp(c->prefix, "H2") == 0 || strcmp(c->prefix, "R1") == 0) {
            /* Absolute: scan forward from position to find that named square */
            return forward_seek(position - 1 + BOARD_SIZE, c->prefix);
        } else {
            /* Relative: next R or next U */
            return forward_seek(position, c->prefix);
        }
    } else if (c->type == CARD_BACKWARD) {
        return backward_seek(position);
    }
    return position;
}

static int dice_roll(int dice_size) {
    return (rand() % dice_size + 1) + (rand() % dice_size + 1);
}

char *solve(int argc, char *argv[]) {
    int dice_size   = (argc > 1) ? atoi(argv[1]) : 6;
    int simulations = (argc > 2) ? atoi(argv[2]) : 1000000;

    srand((unsigned int)time(NULL));

    init_decks();

    int jail = jail_index();
    long long visited[BOARD_SIZE];
    memset(visited, 0, sizeof(visited));

    int position = 0;
    for (int i = 0; i < simulations; i++) {
        position = (position + dice_roll(dice_size)) % BOARD_SIZE;

        if (strncmp(board[position], "CC", 2) == 0) {
            position = next_cc_card(position);
        } else if (strncmp(board[position], "CH", 2) == 0) {
            position = next_ch_card(position);
        } else if (strcmp(board[position], "G2J") == 0) {
            position = jail;
        }

        visited[position]++;
    }

    /* Find top 3 by visit count */
    int top[3] = {-1, -1, -1};
    long long used[BOARD_SIZE];
    memcpy(used, visited, sizeof(visited));

    for (int t = 0; t < 3; t++) {
        long long best = -1;
        int best_idx = 0;
        for (int j = 0; j < BOARD_SIZE; j++) {
            if (used[j] > best) {
                best = used[j];
                best_idx = j;
            }
        }
        top[t] = best_idx;
        used[best_idx] = -1;
    }

    char *result = malloc(7);
    if (!result) return NULL;
    snprintf(result, 7, "%02d%02d%02d", top[0], top[1], top[2]);
    return result;
}

/* Usage: ./file <dice_size> <simulations> [--runs=1] [--show]
 * Output: "<runs> <avg_seconds> <result>" */
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

    char *result = NULL;
    double total = 0.0;
    int rc = 0;

    for (int r = 0; r < runs; r++) {
        struct timespec t0, t1;
        clock_gettime(CLOCK_MONOTONIC, &t0);
        char *cur = solve(solve_argc, solve_argv);
        clock_gettime(CLOCK_MONOTONIC, &t1);
        total += (double)(t1.tv_sec - t0.tv_sec)
               + (double)(t1.tv_nsec - t0.tv_nsec) * 1e-9;
        if (result) free(result);
        result = cur;
    }

    free(solve_argv);
    printf("%d %.17g %s\n", runs, total / (double)runs, result ? result : "");
    if (result) free(result);
    return rc;
}