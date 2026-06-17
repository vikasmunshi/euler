/* Solution to Euler Problem 85: Counting Rectangles. */
#include "runner.h"

/* Count sub-rectangles in a height x width grid by summing placements
 * (height - h + 1) * (width - w + 1) over every sub-rectangle size. */
static int num_rectangles(int height, int width) {
    int count = 0;
    for (int h = 1; h <= height; h++) {
        for (int w = 1; w <= width; w++) {
            count += (height - h + 1) * (width - w + 1);
        }
    }
    return count;
}

/* Brute-force position counting: scan every grid shape, recomputing the
 * exact rectangle count per shape, and keep the area closest to target;
 * O(max_side^2) shapes with O(H*W) work each. */
const char *solve(int argc, char *argv[]) {
    static char _answer[32];
    int max_error = parse_int(argv[1]);
    int max_side  = parse_int(argv[2]);
    int target    = parse_int(argv[3]);

    /* results: store best (height, width, area) keyed by rectangle count.
     * We only need to track the closest to target, so just track best area. */
    int best_area  = -1;
    int best_delta = -1;

    for (int height = 2; height < max_side; height++) {
        for (int width = 2; width < max_side; width++) {
            int num = num_rectangles(height, width);
            int d   = abs(num - target);
            if (best_delta < 0 || d < best_delta) {
                best_delta = d;
                best_area  = height * width;
            }
            if (d <= max_error) {
                goto done;
            }
        }
    }
done:
    { snprintf(_answer, sizeof _answer, "%lld", (long long)((long long)best_area)); return _answer; }
}