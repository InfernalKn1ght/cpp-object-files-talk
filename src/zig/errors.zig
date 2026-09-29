// errors: error union (ошибки как значения) + @panic.
const DivError = error{ByZero};

fn checkedDiv(a: i32, b: i32) DivError!i32 {
    if (b == 0) return error.ByZero;
    return @divTrunc(a, b);
}

export fn try_div(a: i32, b: i32, out: *i32) i32 {
    out.* = checkedDiv(a, b) catch return -1;
    return 0;
}

export fn must_div(a: i32, b: i32) i32 {
    if (b == 0) @panic("division by zero");
    return @divTrunc(a, b);
}
