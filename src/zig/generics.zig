// generics: несколько инстанциаций одного обобщённого кода (i32, i64, f64).
fn sum(comptime T: type, p: [*]const T, n: usize) T {
    var s: T = 0;
    for (p[0..n]) |x| s += x;
    return s;
}

fn maxOf(comptime T: type, p: [*]const T, n: usize) T {
    var m = p[0];
    for (p[1..n]) |x| {
        if (x > m) m = x;
    }
    return m;
}

export fn sum_i32(p: [*]const i32, n: usize) i32 { return sum(i32, p, n); }
export fn sum_i64(p: [*]const i64, n: usize) i64 { return sum(i64, p, n); }
export fn sum_f64(p: [*]const f64, n: usize) f64 { return sum(f64, p, n); }
export fn max_i32(p: [*]const i32, n: usize) i32 { return maxOf(i32, p, n); }
export fn max_i64(p: [*]const i64, n: usize) i64 { return maxOf(i64, p, n); }
export fn max_f64(p: [*]const f64, n: usize) f64 { return maxOf(f64, p, n); }
