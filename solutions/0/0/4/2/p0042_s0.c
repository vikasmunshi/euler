/* Solution to Euler Problem 42: Coded Triangle Numbers. */
#include "runner.h"
#include <math.h>



/* True iff n is triangular, tested via the inverse identity: 8n+1 is a perfect square. */
static int is_triangle_number(int n) {
    double sq = sqrt((double)(8 * n + 1));
    long long sq_int = (long long)round(sq);
    /* Round-trip in 64-bit integers to confirm the root exactly, guarding against fp rounding. */
    return (sq_int * sq_int == (long long)(8 * n + 1));
}

/* Word value: sum of 1-based alphabet positions (A=1..Z=26) of each letter. */
static int word_to_num(const char *word) {
    int sum = 0;
    for (const char *c = word; *c != '\0'; c++) {
        if (*c >= 'A' && *c <= 'Z') {
            sum += (*c - 'A' + 1);
        } else if (*c >= 'a' && *c <= 'z') {
            sum += (*c - 'a' + 1);
        }
    }
    return sum;
}

/* Count words whose value is triangular via the 8n+1-perfect-square test; O(W*L) over W words. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    if (argc < 2) { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
    const char *file_url = argv[1];

    char *text = get_text_file(file_url);
    if (!text) { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }

    long long count = 0;

    char *saveptr = NULL;
    char *token = strtok_r(text, ",", &saveptr);
    while (token != NULL) {
        char word[256];
        int wi = 0;
        for (int i = 0; token[i] != '\0' && wi < 255; i++) {
            char ch = token[i];
            if (ch == '"' || ch == '\r' || ch == '\n' || ch == ' ') continue;
            word[wi++] = ch;
        }
        word[wi] = '\0';

        if (wi > 0) {
            int score = word_to_num(word);
            if (is_triangle_number(score)) {
                count++;
            }
        }

        token = strtok_r(NULL, ",", &saveptr);
    }

    free(text);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(count)); return _answer; }
}