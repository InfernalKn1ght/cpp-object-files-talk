/* Проверка совместимости с C ABI: один и тот же main линкуется с cabi.o каждого языка. */
#include <stdio.h>

typedef struct { int x, y; } Point;
typedef struct { long v[4]; } Big;

extern Point point_add(Point, Point);
extern long point_dot(const Point *, const Point *);
extern long big_sum(Big);

int main(void) {
    Point a = {1, 2}, b = {3, 4};
    Point c = point_add(a, b);
    if (c.x != 4 || c.y != 6) return 1;
    if (point_dot(&a, &b) != 11) return 2;
    Big g = {{1, 2, 3, 4}};
    if (big_sum(g) != 10) return 3;
    puts("cabi ok");
    return 0;
}
