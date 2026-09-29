// errors: исключения C++ (.eh_frame, .gcc_except_table, typeinfo, personality).
#include <stdexcept>

static int checked_div(int a, int b) {
    if (b == 0) throw std::invalid_argument("division by zero");
    return a / b;
}

extern "C" int try_div(int a, int b, int* out) {
    try {
        *out = checked_div(a, b);
        return 0;
    } catch (const std::exception&) {
        return -1;
    }
}

extern "C" int must_div(int a, int b) {
    return checked_div(a, b);  // исключение пересекает границу C-интерфейса (для демонстрации символов)
}
