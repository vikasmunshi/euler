/* Solution to Euler Problem 79: Passcode Derivation. */
#include "runner.h"



#define MAX_DIGITS 10
#define MAX_LINES  200

/*
 * Topological sort by repeated sink removal (Kahn's algorithm, sink-first).
 * Each login "abc" yields ordering constraints a<b and b<c; the deduplicated
 * constraints form a DAG over the distinct digits, stored as a per-node
 * bitmask of successors. Repeatedly removing a node with no active successor
 * and prepending it builds the shortest passcode left-to-right.
 * O(D^2) in the number of distinct digits D (at most 10), effectively constant.
 */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    if (argc < 3) { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    int asked_characters = parse_int(argv[1]);
    const char *file_url = argv[2];

    char *content = get_text_file(file_url);
    if (!content) {
        fprintf(stderr, "Could not open file\n");
        { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    }

    /* Parse and deduplicate lines; repeated logins add no ordering information */
    char lines[MAX_LINES][16];
    int line_count = 0;

    char *p = content;
    while (*p) {
        while (*p == '\r' || *p == '\n' || *p == ' ') p++;
        if (*p == '\0') break;
        int li = 0;
        char token[16];
        while (*p && *p != '\r' && *p != '\n' && li < 15) {
            token[li++] = *p++;
        }
        token[li] = '\0';
        if (li == 0) continue;
        int dup = 0;
        for (int i = 0; i < line_count; i++) {
            if (strcmp(lines[i], token) == 0) { dup = 1; break; }
        }
        if (!dup && line_count < MAX_LINES) {
            strncpy(lines[line_count], token, 15);
            lines[line_count][15] = '\0';
            line_count++;
        }
    }
    free(content);

    /* Collect distinct characters; their indices become the DAG node ids */
    char chars[MAX_DIGITS];
    int num_chars = 0;
    for (int i = 0; i < line_count; i++) {
        for (int j = 0; lines[i][j]; j++) {
            char c = lines[i][j];
            int found = 0;
            for (int k = 0; k < num_chars; k++) {
                if (chars[k] == c) { found = 1; break; }
            }
            if (!found && num_chars < MAX_DIGITS) chars[num_chars++] = c;
        }
    }

    /* Build successor graph: bit j of successor[i] set means digit i precedes digit j */
    unsigned int successor[MAX_DIGITS] = {0};
    int num_pairs = asked_characters - 1; /* consecutive pairs per login; generalises beyond 3 */

    for (int i = 0; i < line_count; i++) {
        for (int j = 0; j < num_pairs; j++) {
            if (lines[i][j] == '\0' || lines[i][j + 1] == '\0') break;
            char a = lines[i][j];
            char b = lines[i][j + 1];
            int ai = -1, bi = -1;
            for (int k = 0; k < num_chars; k++) {
                if (chars[k] == a) ai = k;
                if (chars[k] == b) bi = k;
            }
            if (ai >= 0 && bi >= 0) {
                successor[ai] |= (1u << bi);
            }
        }
    }

    /* Reverse topological sort: a sink (no active successor) belongs furthest right */
    int active[MAX_DIGITS];
    for (int i = 0; i < num_chars; i++) active[i] = 1;

    char passcode[MAX_DIGITS + 1];
    int passcode_len = 0;
    passcode[0] = '\0';

    int remaining = num_chars;
    while (remaining > 0) {
        /* Active mask lets the sink test reduce to one bitwise AND per node */
        unsigned int active_mask = 0;
        for (int i = 0; i < num_chars; i++) {
            if (active[i]) active_mask |= (1u << i);
        }

        int found = -1;
        for (int i = 0; i < num_chars; i++) {
            if (!active[i]) continue;
            if ((successor[i] & active_mask) == 0) {
                found = i;
                break;
            }
        }
        if (found < 0) {
            fprintf(stderr, "Cycle detected in constraints\n");
            { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
        }

        /* Prepend chars[found]: removing sinks yields rightmost elements first */
        for (int i = passcode_len; i >= 0; i--) {
            passcode[i + 1] = passcode[i];
        }
        passcode[0] = chars[found];
        passcode_len++;

        active[found] = 0;
        remaining--;
    }

    { snprintf(_answer, sizeof _answer, "%lld", (long long)((long long)atoll(passcode))); return _answer; }
}