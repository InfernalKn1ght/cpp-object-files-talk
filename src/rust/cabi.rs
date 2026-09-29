// cabi: структуры по значению через C ABI (SysV: Point в регистре, Big в памяти).
#[repr(C)]
#[derive(Clone, Copy)]
pub struct Point {
    pub x: i32,
    pub y: i32,
}

#[repr(C)]
pub struct Big {
    pub v: [i64; 4],
}

#[no_mangle]
pub extern "C" fn point_add(a: Point, b: Point) -> Point {
    Point { x: a.x + b.x, y: a.y + b.y }
}

#[no_mangle]
pub extern "C" fn point_dot(a: *const Point, b: *const Point) -> i64 {
    let (a, b) = unsafe { (&*a, &*b) };
    (a.x as i64) * (b.x as i64) + (a.y as i64) * (b.y as i64)
}

#[no_mangle]
pub extern "C" fn big_sum(b: Big) -> i64 {
    b.v[0] + b.v[1] + b.v[2] + b.v[3]
}
