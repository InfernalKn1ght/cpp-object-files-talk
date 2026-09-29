// cabi: структуры по значению через C ABI (SysV: Point в регистре, Big в памяти).
struct Point { int x; int y; };
struct Big { long v[4]; };

extern "C" {
Point point_add(Point a, Point b) { return {a.x + b.x, a.y + b.y}; }
long point_dot(const Point* a, const Point* b) {
    return (long)a->x * b->x + (long)a->y * b->y;
}
long big_sum(Big b) { return b.v[0] + b.v[1] + b.v[2] + b.v[3]; }
}
