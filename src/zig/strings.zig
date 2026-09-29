// strings: работа с байтовыми буферами и строковым литералом (.rodata).
export fn count_char(s: [*]const u8, n: usize, c: u8) usize {
    var k: usize = 0;
    for (s[0..n]) |x| {
        if (x == c) k += 1;
    }
    return k;
}

export fn to_upper_inplace(s: [*]u8, n: usize) void {
    for (s[0..n]) |*x| {
        if (x.* >= 'a' and x.* <= 'z') x.* -= 32;
    }
}

export fn greeting() [*:0]const u8 {
    return "hello, object file";
}
