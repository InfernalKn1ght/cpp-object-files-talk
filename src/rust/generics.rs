// generics: несколько инстанциаций одного обобщённого кода (i32, i64, f64).
use core::ops::AddAssign;

pub fn sum<T: Copy + Default + AddAssign>(xs: &[T]) -> T {
    let mut s = T::default();
    for &x in xs {
        s += x;
    }
    s
}

pub fn max_of<T: Copy + PartialOrd>(xs: &[T]) -> T {
    let mut m = xs[0];
    for &x in xs {
        if x > m {
            m = x;
        }
    }
    m
}

macro_rules! export_pair {
    ($sum:ident, $max:ident, $t:ty) => {
        #[no_mangle]
        pub extern "C" fn $sum(p: *const $t, n: usize) -> $t {
            sum(unsafe { core::slice::from_raw_parts(p, n) })
        }
        #[no_mangle]
        pub extern "C" fn $max(p: *const $t, n: usize) -> $t {
            max_of(unsafe { core::slice::from_raw_parts(p, n) })
        }
    };
}

export_pair!(sum_i32, max_i32, i32);
export_pair!(sum_i64, max_i64, i64);
export_pair!(sum_f64, max_f64, f64);
