// strings: работа с байтовыми буферами и строковым литералом (.rodata).
#[no_mangle]
pub extern "C" fn count_char(s: *const u8, n: usize, c: u8) -> usize {
    let s = unsafe { core::slice::from_raw_parts(s, n) };
    s.iter().filter(|&&b| b == c).count()
}

#[no_mangle]
pub extern "C" fn to_upper_inplace(s: *mut u8, n: usize) {
    let s = unsafe { core::slice::from_raw_parts_mut(s, n) };
    for b in s.iter_mut() {
        if b.is_ascii_lowercase() {
            *b -= 32;
        }
    }
}

#[no_mangle]
pub extern "C" fn greeting() -> *const u8 {
    b"hello, object file\0".as_ptr()
}
