// errors: Result как значение + panic (раскрутка стека или abort, см. -C panic).
#[derive(Debug)]
pub enum DivError {
    ByZero,
}

pub fn checked_div(a: i32, b: i32) -> Result<i32, DivError> {
    if b == 0 {
        Err(DivError::ByZero)
    } else {
        Ok(a / b)
    }
}

#[no_mangle]
pub extern "C" fn try_div(a: i32, b: i32, out: *mut i32) -> i32 {
    match checked_div(a, b) {
        Ok(v) => {
            unsafe { *out = v };
            0
        }
        Err(_) => -1,
    }
}

#[no_mangle]
pub extern "C" fn must_div(a: i32, b: i32) -> i32 {
    if b == 0 {
        panic!("division by zero");
    }
    a / b
}
