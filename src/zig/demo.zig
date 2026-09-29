// demo: пример со слайдов. Структура-пространство имён, comptime-дженерик, export.
const geom = struct {
    fn area(w: i32, h: i32) i32 {
        return w * h;
    }
};

fn add(comptime T: type, a: T, b: T) T {
    return a + b;
}

export fn c_area(w: i32, h: i32) i32 {
    return geom.area(w, h);
}

export fn add_i32(a: i32, b: i32) i32 {
    return add(i32, a, b);
}
