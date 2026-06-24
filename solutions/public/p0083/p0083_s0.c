/* Solution to Euler Problem 83: Path Sum: Four Ways. */
#include "runner.h"

#define MAX_SIZE 80
#define MAX_CONTENT (1 << 20)



static const char *default_content =
    "131, 673, 234, 103, 18\n"
    "201, 96, 342, 965, 150\n"
    "630, 803, 746, 422, 111\n"
    "537, 699, 497, 121, 956\n"
    "805, 732, 524, 37, 331\n";

/* Minimal four-directional path sum via Dijkstra with a linear minimum scan; O(V^2) = O(N^4).
   Four-directional movement admits cycles, so single-pass DP fails; non-negative cell weights
   make Dijkstra exact. Nodes are flattened to row-major indices for contiguous, cache-friendly
   per-node arrays, and the search stops as soon as the bottom-right target is finalised. */
static long long path_sum_four_ways(const char *content) {
    int matrix[MAX_SIZE][MAX_SIZE];
    int size = 0;

    const char *p = content;
    while (*p) {
        while (*p == '\r' || *p == '\n') p++;
        if (!*p) break;
        int col = 0;
        while (*p && *p != '\n' && *p != '\r') {
            while (*p == ' ') p++;
            if (!*p || *p == '\n' || *p == '\r') break;
            matrix[size][col++] = atoi(p);
            while (*p && *p != ',' && *p != '\n' && *p != '\r') p++;
            if (*p == ',') p++;
        }
        if (col > 0) size++;
    }

    /* Concrete sentinel that provably exceeds any path cost; avoids INT_MAX overflow on relaxation. */
    long long infinity = 1;
    for (int r = 0; r < size; r++)
        for (int c = 0; c < size; c++)
            infinity += matrix[r][c];

    int n = size * size;
    long long *dist = malloc((size_t)n * sizeof(long long));
    int *visited = malloc((size_t)n * sizeof(int));
    if (!dist || !visited) { free(dist); free(visited); return -1; }

    for (int i = 0; i < n; i++) {
        dist[i] = infinity;
        visited[i] = 0;
    }
    dist[0] = matrix[0][0];

    int target = (size - 1) * size + (size - 1);

    while (!visited[target]) {
        /* Linear scan for the closest unfinalised node (the priority-queue step done naively). */
        int cur = -1;
        long long cur_dist = infinity;
        for (int i = 0; i < n; i++) {
            if (!visited[i] && dist[i] < cur_dist) {
                cur_dist = dist[i];
                cur = i;
            }
        }
        if (cur == -1) break;

        visited[cur] = 1;
        if (cur == target) break;

        int crow = cur / size;
        int ccol = cur % size;

        /* Direction vectors enumerate up/down/left/right in one bounds-checked loop. */
        int drow[4] = {-1, 1, 0, 0};
        int dcol[4] = {0, 0, -1, 1};
        for (int d = 0; d < 4; d++) {
            int nr = crow + drow[d];
            int nc = ccol + dcol[d];
            if (nr < 0 || nr >= size || nc < 0 || nc >= size) continue;
            int ni = nr * size + nc;
            if (visited[ni]) continue;
            long long new_dist = dist[cur] + matrix[nr][nc];
            if (new_dist < dist[ni])
                dist[ni] = new_dist;
        }
    }

    long long result = dist[target];
    free(dist);
    free(visited);
    return result;
}

const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    const char *content = NULL;
    char *allocated = NULL;

    if (argc >= 2 && argv[1][0] != '\0') {
        allocated = get_text_file(argv[1]);
        if (!allocated) {
            fprintf(stderr, "Failed to load file: %s\n", argv[1]);
            { snprintf(_answer, sizeof _answer, "%lld", (long long)(-1)); return _answer; }
        }
        content = allocated;
    }
    if (!content)
        content = default_content;

    long long result = path_sum_four_ways(content);
    free(allocated);
    { snprintf(_answer, sizeof _answer, "%lld", (long long)(result)); return _answer; }
}