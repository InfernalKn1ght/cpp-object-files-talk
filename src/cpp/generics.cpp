// generics: несколько инстанциаций одного обобщённого кода (int, long long, double).
#include <cstddef>

template <class T>
T sum(const T* p, std::size_t n) {
    T s{};
    for (std::size_t i = 0; i < n; ++i) s += p[i];
    return s;
}

template <class T>
T max_of(const T* p, std::size_t n) {
    T m = p[0];
    for (std::size_t i = 1; i < n; ++i)
        if (p[i] > m) m = p[i];
    return m;
}

template int sum<int>(const int*, std::size_t);
template long long sum<long long>(const long long*, std::size_t);
template double sum<double>(const double*, std::size_t);
template int max_of<int>(const int*, std::size_t);
template long long max_of<long long>(const long long*, std::size_t);
template double max_of<double>(const double*, std::size_t);

extern "C" {
int sum_i32(const int* p, std::size_t n) { return sum<int>(p, n); }
long long sum_i64(const long long* p, std::size_t n) { return sum<long long>(p, n); }
double sum_f64(const double* p, std::size_t n) { return sum<double>(p, n); }
int max_i32(const int* p, std::size_t n) { return max_of<int>(p, n); }
long long max_i64(const long long* p, std::size_t n) { return max_of<long long>(p, n); }
double max_f64(const double* p, std::size_t n) { return max_of<double>(p, n); }
}
