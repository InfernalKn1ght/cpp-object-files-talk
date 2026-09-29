// demo: пример со слайдов. Модуль, дженерик, C-интерфейс.
// Edition 2021: атрибут пишется #[no_mangle]; в edition 2024 нужно #[unsafe(no_mangle)].
pub mod geom {
    pub fn area(w: i32, h: i32) -> i32 {
        w * h
    }
}

pub fn add<T: core::ops::Add<Output = T>>(a: T, b: T) -> T {
    a + b
}

#[no_mangle]
pub extern "C" fn c_area(w: i32, h: i32) -> i32 {
    geom::area(w, h)
}

#[no_mangle]
pub extern "C" fn add_i32(a: i32, b: i32) -> i32 {
    add(a, b)
}
