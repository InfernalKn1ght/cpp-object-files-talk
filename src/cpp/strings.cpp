// strings: работа с байтовыми буферами и строковым литералом (.rodata).
#include <cstddef>

extern "C" {
std::size_t count_char(const unsigned char* s, std::size_t n, unsigned char c) {
    std::size_t k = 0;
    for (std::size_t i = 0; i < n; ++i)
        if (s[i] == c) ++k;
    return k;
}

void to_upper_inplace(unsigned char* s, std::size_t n) {
    for (std::size_t i = 0; i < n; ++i)
        if (s[i] >= 'a' && s[i] <= 'z') s[i] -= 32;
}

const char* greeting() { return "hello, object file"; }
}
