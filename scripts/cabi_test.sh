#!/usr/bin/env bash
# Check C ABI compatibility: a common C main is linked with each language's cabi.o (O2 mode).
#   scripts/cabi_test.sh
set -uo pipefail
cd "$(dirname "$0")/.."
mkdir -p build
python3 scripts/collect.py --build-only --progs cabi --modes O2 >/dev/null 2>&1 || true
CC=${CC:-cc}
TMP=$(mktemp -d)   # binaries are built in a temporary directory (the repository may be noexec)
trap 'rm -rf "$TMP"' EXIT
$CC -c -O1 tests/cabi_main.c -o build/cabi_main.o || exit 1
rc=0
for lang in cpp rust zig; do
  obj=build/$lang/O2/cabi.o
  if [ ! -f "$obj" ]; then echo "$lang: skipped (object file not found)"; continue; fi
  if $CC build/cabi_main.o "$obj" -o "$TMP/cabi_test_$lang" 2>"build/link_$lang.log"; then
    if "$TMP/cabi_test_$lang" >/dev/null; then
      echo "$lang: C ABI OK (struct in register, struct in memory, pointers)"
    else
      echo "$lang: RUNTIME ERROR, code $?"; rc=1
    fi
  else
    echo "$lang: LINK ERROR, see build/link_$lang.log"; rc=1
  fi
done
exit $rc
