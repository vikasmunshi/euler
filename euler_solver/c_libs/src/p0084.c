/*******************************************************************************
 * File: p0097.c
 *
 * Description: C implementation for Project Euler problem 84 (Monopoly Odds).
 * Exports a function usable via ctypes from Python.
 *
 * Author: Project Euler Solution
 * Created: 2025-08-23
 *
 * Copyright (c) 2025. All rights reserved.
 ******************************************************************************/
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

// C API:
// int monopoly_simulate(int dice_size, int simulations, long long* counts_out)
// - dice_size: sides on each die (e.g., 4 or 6)
// - simulations: number of rolls to simulate
// - counts_out: pointer to array[40] of long long to store visit counts per board index
// Returns 0 on success, non-zero on invalid arguments.

#define BOARD_SIZE 40

static const char* BOARD[BOARD_SIZE] = {
    "GO", "A1", "CC1", "A2", "T1", "R1", "B1", "CH1", "B2", "B3",
    "JAIL", "C1", "U1", "C2", "C3", "R2", "D1", "CC2", "D2", "D3",
    "FP", "E1", "CH2", "E2", "E3", "R3", "F1", "F2", "U2", "F3",
    "G2J", "G1", "G2", "CC3", "G3", "R4", "CH3", "H1", "T2", "H2"
};

// Helpers to find next index with name starting with a prefix
static int starts_with(const char* s, const char* prefix) {
    while (*prefix) {
        if (*s != *prefix) return 0;
        ++s; ++prefix;
    }
    return 1;
}

static int index_of_label(const char* label) {
    for (int i = 0; i < BOARD_SIZE; ++i) {
        if (strcmp(BOARD[i], label) == 0) return i;
    }
    return -1;
}

// Simple deterministic RNG using linear congruential generator to avoid platform-specific rand() differences
static uint64_t rng_state = 88172645463393265ULL; // arbitrary seed
static inline uint32_t lcg_rand(void) {
    rng_state = rng_state * 2862933555777941757ULL + 3037000493ULL;
    return (uint32_t)(rng_state >> 32);
}

static inline int roll_die(int dice_size) {
    // return value in [1, dice_size]
    return (int)(lcg_rand() % (uint32_t)dice_size) + 1;
}

// Card stacks: we model as arrays of 16 movement codes and a current index; we shuffle once at start.
// Movement encoding:
// 0 = Null (stay)
// 1 = Go to label (GO)
// 2 = Go to label (JAIL)
// 3 = Go to label (C1)
// 4 = Go to label (E3)
// 5 = Go to label (H2)
// 6 = Go to label (R1)
// 7 = Go to next R (railway)
// 8 = Go to next R (railway)
// 9 = Go to next U (utility)
// 10 = Go back 3 squares
// Mapping mirrors the given Python setup for CH; CC only uses 1 and 2 plus nulls.

typedef struct {
    int cards[16];
    int idx;
} CardStack;

static void shuffle_cards(CardStack* cs) {
    // Fisher-Yates using our LCG
    for (int i = 15; i > 0; --i) {
        int j = (int)(lcg_rand() % (uint32_t)(i + 1));
        int tmp = cs->cards[i];
        cs->cards[i] = cs->cards[j];
        cs->cards[j] = tmp;
    }
    cs->idx = 0;
}

static int next_card(CardStack* cs) {
    int v = cs->cards[cs->idx];
    cs->idx = (cs->idx + 1) % 16;
    return v;
}

static void init_cc(CardStack* cc) {
    // 16 cards: [GO, JAIL] + 14 Null
    int k = 0;
    cc->cards[k++] = 1; // GO
    cc->cards[k++] = 2; // JAIL
    while (k < 16) cc->cards[k++] = 0; // Null
    shuffle_cards(cc);
}

static void init_ch(CardStack* ch) {
    // [GO, JAIL, C1, E3, H2, R1, R, R, U, Back3] + 6 Nulls
    int arr[16] = {1,2,3,4,5,6,7,7,9,10,0,0,0,0,0,0};
    for (int i = 0; i < 16; ++i) ch->cards[i] = arr[i];
    shuffle_cards(ch);
}

static int apply_ch_move(int position, int code) {
    switch (code) {
        case 0: // Null
            return position;
        case 1: // GO
            return index_of_label("GO");
        case 2: // JAIL
            return index_of_label("JAIL");
        case 3: // C1
            return index_of_label("C1");
        case 4: // E3
            return index_of_label("E3");
        case 5: // H2
            return index_of_label("H2");
        case 6: // R1
            return index_of_label("R1");
        case 7: { // next R
            int pos = position;
            while (!starts_with(BOARD[pos], "R")) {
                pos = (pos + 1) % BOARD_SIZE;
            }
            return pos;
        }
        case 9: { // next U
            int pos = position;
            while (!starts_with(BOARD[pos], "U")) {
                pos = (pos + 1) % BOARD_SIZE;
            }
            return pos;
        }
        case 10: { // back 3
            int pos = (position - 3);
            pos %= BOARD_SIZE; if (pos < 0) pos += BOARD_SIZE;
            return pos;
        }
        default:
            return position;
    }
}

static int apply_cc_move(int position, int code) {
    switch (code) {
        case 0: return position; // Null
        case 1: return index_of_label("GO");
        case 2: return index_of_label("JAIL");
        default: return position;
    }
}

int monopoly_simulate(int dice_size, int simulations, long long* counts_out) {
    if (dice_size <= 0 || simulations < 0 || counts_out == NULL) return 1;

    // zero counts
    for (int i = 0; i < BOARD_SIZE; ++i) counts_out[i] = 0;

    // initialize RNG with fixed seed for determinism
    rng_state = 1469598103934665603ULL; // FNV offset basis as seed

    // init cards
    CardStack cc, ch;
    init_cc(&cc);
    init_ch(&ch);

    int position = 0;
    const int JAIL = index_of_label("JAIL");

    for (int i = 0; i < simulations; ++i) {
        int move = roll_die(dice_size) + roll_die(dice_size);
        position = (position + move) % BOARD_SIZE;

        const char* label = BOARD[position];
        if (label[0] == 'C' && label[1] == 'C') {
            int code = next_card(&cc);
            position = apply_cc_move(position, code);
        } else if (label[0] == 'C' && label[1] == 'H') {
            int code = next_card(&ch);
            position = apply_ch_move(position, code);
        } else if (strcmp(label, "G2J") == 0) {
            position = JAIL;
        }
        counts_out[position] += 1;
    }

    return 0;
}
