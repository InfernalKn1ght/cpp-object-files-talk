// cabi: структуры по значению через C ABI (SysV: Point в регистре, Big в памяти).
const Point = extern struct { x: i32, y: i32 };
const Big = extern struct { v: [4]i64 };

export fn point_add(a: Point, b: Point) Point {
    return .{ .x = a.x + b.x, .y = a.y + b.y };
}

export fn point_dot(a: *const Point, b: *const Point) i64 {
    return @as(i64, a.x) * @as(i64, b.x) + @as(i64, a.y) * @as(i64, b.y);
}

export fn big_sum(b: Big) i64 {
    return b.v[0] + b.v[1] + b.v[2] + b.v[3];
}
