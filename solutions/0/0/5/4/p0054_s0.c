/* Solution to Euler Problem 54: Poker Hands. */
#include <libgen.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

static const char *VALUES = "23456789TJQKA";

typedef enum {
    HIGH_CARD       = 0,
    ONE_PAIR        = 1,
    TWO_PAIRS       = 2,
    THREE_OF_A_KIND = 3,
    STRAIGHT        = 4,
    FLUSH           = 5,
    FULL_HOUSE      = 6,
    FOUR_OF_A_KIND  = 7,
    STRAIGHT_FLUSH  = 8,
    ROYAL_FLUSH     = 9
} PokerRank;

typedef struct {
    PokerRank rank;
    int tie_breakers[5];
    int tb_count;
} HandRank;

static int card_value(char c) {
    const char *p = strchr(VALUES, c);
    if (!p) return -1;
    return (int)(p - VALUES);
}

static int suit_order(char s) {
    switch (s) {
        case 'C': return 0;
        case 'D': return 1;
        case 'H': return 2;
        case 'S': return 3;
        default:  return -1;
    }
}

static int cmp_desc(const void *a, const void *b) {
    return *(const int *)b - *(const int *)a;
}

static HandRank evaluate_hand(char cards[5][3]) {
    int values[5];
    char suits[5];
    HandRank hr;
    memset(&hr, 0, sizeof(hr));

    for (int i = 0; i < 5; i++) {
        values[i] = card_value(cards[i][0]);
        suits[i]  = cards[i][1];
    }

    int is_flush = 1;
    for (int i = 1; i < 5; i++) {
        if (suits[i] != suits[0]) { is_flush = 0; break; }
    }

    int sorted_vals[5];
    memcpy(sorted_vals, values, sizeof(values));
    for (int i = 0; i < 5; i++)
        for (int j = i + 1; j < 5; j++)
            if (sorted_vals[j] < sorted_vals[i]) {
                int tmp = sorted_vals[i];
                sorted_vals[i] = sorted_vals[j];
                sorted_vals[j] = tmp;
            }

    int distinct = 1;
    for (int i = 1; i < 5; i++)
        if (sorted_vals[i] != sorted_vals[i - 1]) distinct++;

    int is_straight = (distinct == 5) && (sorted_vals[4] - sorted_vals[0] == 4);

    if (is_straight && is_flush) {
        if (sorted_vals[0] == 8) {
            hr.rank = ROYAL_FLUSH;
            hr.tie_breakers[0] = suit_order(suits[0]);
            hr.tb_count = 1;
        } else {
            hr.rank = STRAIGHT_FLUSH;
            hr.tie_breakers[0] = sorted_vals[4];
            hr.tb_count = 1;
        }
        return hr;
    }

    /* Count unique values */
    int uvals[5], ucounts[5], ucount = 0;
    for (int i = 0; i < 5; i++) {
        int found = 0;
        for (int j = 0; j < ucount; j++) {
            if (uvals[j] == values[i]) {
                ucounts[j]++;
                found = 1;
                break;
            }
        }
        if (!found) {
            uvals[ucount] = values[i];
            ucounts[ucount] = 1;
            ucount++;
        }
    }

    /* Sort by count desc, then value desc */
    for (int i = 0; i < ucount; i++) {
        for (int j = i + 1; j < ucount; j++) {
            int swap = 0;
            if (ucounts[j] > ucounts[i]) swap = 1;
            else if (ucounts[j] == ucounts[i] && uvals[j] > uvals[i]) swap = 1;
            if (swap) {
                int tmp = ucounts[i]; ucounts[i] = ucounts[j]; ucounts[j] = tmp;
                tmp = uvals[i]; uvals[i] = uvals[j]; uvals[j] = tmp;
            }
        }
    }

    if (ucounts[0] == 4) {
        hr.rank = FOUR_OF_A_KIND;
        hr.tie_breakers[0] = uvals[0];
        hr.tie_breakers[1] = uvals[1];
        hr.tb_count = 2;
        return hr;
    }

    if (ucounts[0] == 3 && ucounts[1] == 2) {
        hr.rank = FULL_HOUSE;
        hr.tie_breakers[0] = uvals[0];
        hr.tie_breakers[1] = uvals[1];
        hr.tb_count = 2;
        return hr;
    }

    if (is_flush) {
        hr.rank = FLUSH;
        int sv[5];
        memcpy(sv, values, sizeof(values));
        qsort(sv, 5, sizeof(int), cmp_desc);
        for (int i = 0; i < 5; i++) hr.tie_breakers[i] = sv[i];
        hr.tb_count = 5;
        return hr;
    }

    if (is_straight) {
        hr.rank = STRAIGHT;
        hr.tie_breakers[0] = sorted_vals[4];
        hr.tb_count = 1;
        return hr;
    }

    if (ucounts[0] == 3) {
        hr.rank = THREE_OF_A_KIND;
        hr.tie_breakers[0] = uvals[0];
        int kickers[2], ki = 0;
        for (int i = 0; i < 5; i++) {
            if (values[i] != uvals[0]) kickers[ki++] = values[i];
        }
        if (ki == 2 && kickers[0] < kickers[1]) {
            int tmp = kickers[0]; kickers[0] = kickers[1]; kickers[1] = tmp;
        }
        hr.tie_breakers[1] = kickers[0];
        hr.tie_breakers[2] = kickers[1];
        hr.tb_count = 3;
        return hr;
    }

    if (ucount >= 2 && ucounts[0] == 2 && ucounts[1] == 2) {
        int p0 = uvals[0], p1 = uvals[1];
        int high_pair = (p0 > p1) ? p0 : p1;
        int low_pair  = (p0 > p1) ? p1 : p0;
        int kicker = -1;
        for (int i = 0; i < 5; i++) {
            if (values[i] != high_pair && values[i] != low_pair) {
                kicker = values[i];
                break;
            }
        }
        hr.rank = TWO_PAIRS;
        hr.tie_breakers[0] = high_pair;
        hr.tie_breakers[1] = low_pair;
        hr.tie_breakers[2] = kicker;
        hr.tb_count = 3;
        return hr;
    }

    if (ucounts[0] == 2) {
        hr.rank = ONE_PAIR;
        hr.tie_breakers[0] = uvals[0];
        int kickers[3], ki = 0;
        for (int i = 0; i < 5; i++) {
            if (values[i] != uvals[0]) kickers[ki++] = values[i];
        }
        for (int i = 0; i < ki; i++)
            for (int j = i + 1; j < ki; j++)
                if (kickers[j] > kickers[i]) {
                    int tmp = kickers[i]; kickers[i] = kickers[j]; kickers[j] = tmp;
                }
        for (int i = 0; i < ki; i++) hr.tie_breakers[1 + i] = kickers[i];
        hr.tb_count = 1 + ki;
        return hr;
    }

    hr.rank = HIGH_CARD;
    int sv[5];
    memcpy(sv, values, sizeof(values));
    qsort(sv, 5, sizeof(int), cmp_desc);
    for (int i = 0; i < 5; i++) hr.tie_breakers[i] = sv[i];
    hr.tb_count = 5;
    return hr;
}

static int hand_rank_gt(HandRank *hr1, HandRank *hr2) {
    if (hr1->rank != hr2->rank)
        return hr1->rank > hr2->rank;
    int len = hr1->tb_count < hr2->tb_count ? hr1->tb_count : hr2->tb_count;
    for (int i = 0; i < len; i++) {
        if (hr1->tie_breakers[i] != hr2->tie_breakers[i])
            return hr1->tie_breakers[i] > hr2->tie_breakers[i];
    }
    return 0;
}

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

long long solve(int argc, char *argv[]) {
    const char *file_url = (argc > 1) ? argv[1] : "";

    char *content = get_text_file(file_url);
    if (!content) {
        fprintf(stderr, "Could not open poker file\n");
        return -1;
    }

    long long p1_wins = 0;
    char *saveptr = NULL;
    char *line = strtok_r(content, "\n", &saveptr);
    while (line) {
        /* Skip empty lines */
        int all_ws = 1;
        for (int k = 0; line[k]; k++)
            if (line[k] != ' ' && line[k] != '\r' && line[k] != '\t') { all_ws = 0; break; }
        if (all_ws) { line = strtok_r(NULL, "\n", &saveptr); continue; }

        char tokens[10][4];
        int n = 0;
        char line_copy[256];
        strncpy(line_copy, line, sizeof(line_copy) - 1);
        line_copy[sizeof(line_copy) - 1] = '\0';

        char *inner_save = NULL;
        char *tok = strtok_r(line_copy, " \r\t", &inner_save);
        while (tok && n < 10) {
            strncpy(tokens[n], tok, 3);
            tokens[n][3] = '\0';
            n++;
            tok = strtok_r(NULL, " \r\t", &inner_save);
        }

        if (n < 10) { line = strtok_r(NULL, "\n", &saveptr); continue; }

        char p1cards[5][3], p2cards[5][3];
        for (int i = 0; i < 5; i++) {
            strncpy(p1cards[i], tokens[i], 2); p1cards[i][2] = '\0';
            strncpy(p2cards[i], tokens[i + 5], 2); p2cards[i][2] = '\0';
        }

        HandRank hr1 = evaluate_hand(p1cards);
        HandRank hr2 = evaluate_hand(p2cards);

        if (hand_rank_gt(&hr1, &hr2)) p1_wins++;

        line = strtok_r(NULL, "\n", &saveptr);
    }

    free(content);
    return p1_wins;
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