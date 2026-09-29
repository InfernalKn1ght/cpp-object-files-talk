# Summary (sum across the corpus)

## Sizes, bytes

| Language / mode | total | .text | .data+.rodata | .debug_* | .eh_frame |
|---|---:|---:|---:|---:|---:|
| C++ O2 | 14232 | 3653 | 164 | 0 | 720 |
| C++ O2g | 53640 | 3653 | 164 | 21344 | 720 |
| Rust O2 | 14592 | 2250 | 349 | 0 | 560 |
| Rust O2g | 82104 | 2250 | 349 | 33998 | 560 |
| Zig O2 | 311256 | 105851 | 43793 | 0 | 9432 |
| Zig O2g | 4311752 | 333163 | 63637 | 2182518 | 13600 |

## Sections, symbols, relocations

| Language / mode | sections | def/undef | weak | relocations | main type |
|---|---:|---:|---:|---:|---|
| C++ O2 | 69 | 55/11 | 8 | 56 (debug: 0) | R_X86_64_PC32 |
| C++ O2g | 132 | 95/11 | 8 | 571 (debug: 515) | R_X86_64_32 |
| Rust O2 | 83 | 62/7 | 2 | 53 (debug: 0) | R_X86_64_PC32 |
| Rust O2g | 141 | 91/7 | 2 | 1242 (debug: 1189) | R_X86_64_32 |
| Zig O2 | 53 | 168/7 | 0 | 5878 (debug: 0) | R_X86_64_PC32 |
| Zig O2g | 112 | 765/8 | 1 | 69823 (debug: 61527) | R_X86_64_64 |

## Compilation time and linker load

Time: sum of medians across programs. Max RSS: maximum across programs. `.text*` sections and COMDAT groups show how many units `--gc-sections` can discard.

| Language / mode | time, ms | Max RSS, MB | .text* sections | COMDAT groups | undef |
|---|---:|---:|---:|---:|---:|
| C++ O2 | 535 | 177 | 12 | 8 | 11 |
| C++ O2g | 546 | 178 | 12 | 8 | 11 |
| Rust O2 | 224 | 188 | 21 | 2 | 7 |
| Rust O2g | 247 | 189 | 21 | 2 | 7 |
| Zig O2 | 4457 | 214 | 6 | 0 | 7 |
| Zig O2g | 13615 | 322 | 6 | 0 | 8 |

## Типы релокаций, режим O2g

| Тип | C++ | Rust | Zig |
|---|---:|---:|---:|
| R_X86_64_32 | 467 | 728 | 27638 |
| R_X86_64_64 | 50 | 467 | 34141 |
| R_X86_64_DTPOFF32 | 0 | 0 | 19 |
| R_X86_64_DTPOFF64 | 0 | 0 | 3 |
| R_X86_64_GOTPCREL | 0 | 11 | 1 |
| R_X86_64_PC32 | 38 | 36 | 7661 |
| R_X86_64_PLT32 | 12 | 0 | 355 |
| R_X86_64_REX_GOTPCRELX | 4 | 0 | 1 |
| R_X86_64_TLSLD | 0 | 0 | 4 |
