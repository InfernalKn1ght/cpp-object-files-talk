// demo: пример со слайдов. Пространство имён, шаблон, C-интерфейс.
namespace geom {
int area(int w, int h) { return w * h; }
}

template <class T>
T add(T a, T b) { return a + b; }

// Явная инстанциация: гарантирует weak/COMDAT-символ add<int>.
template int add<int>(int, int);

extern "C" int c_area(int w, int h) { return geom::area(w, h); }
extern "C" int add_i32(int a, int b) { return add<int>(a, b); }
