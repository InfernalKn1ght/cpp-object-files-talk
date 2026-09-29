#!/usr/bin/env bash
# Live presentation demo: what is inside the demo example object file.
#   scripts/demo.sh [cpp|rust|zig|all] [режим]      режим по умолчанию O0g (есть -g, символы не вырезаны)
#   PAUSE=1 scripts/demo.sh cpp O2g                  wait for Enter before each step
set -uo pipefail
cd "$(dirname "$0")/.."

LANGS=${1:-all}
MODE=${2:-O0g}
[ "$LANGS" = all ] && LANGS="cpp rust zig"

B=$'\e[1m'; D=$'\e[2m'; R=$'\e[0m'
step() { echo; echo "${B}== $* ==${R}"; if [ "${PAUSE:-0}" = 1 ]; then read -r -p "[Enter] " _; fi; }
sh_()  { echo "${D}\$ $1${R}"; bash -c "$1" 2>&1 || true; }

for lang in $LANGS; do
  obj=build/$lang/$MODE/demo.o
  if [ ! -f "$obj" ]; then
    python3 scripts/collect.py --build-only --langs "$lang" --progs demo --modes "$MODE" >/dev/null 2>&1 || true
  fi
  if [ ! -f "$obj" ]; then echo "${B}[$lang]${R} skipped: $obj not found (compiler missing or build error)"; continue; fi

  echo; echo "${B}################  $lang  ($MODE)  ################${R}"
  step "$lang: section sizes"
  sh_ "size -A $obj"

  step "$lang: section table"
  sh_ "readelf -SW $obj | grep -E '\\.(text|data|bss|rodata|symtab|strtab|group|rela|eh_frame|gcc_except|debug)'"

  step "$lang: symbols as-is (mangled)"
  sh_ "nm $obj"

  step "$lang: symbols after demangling"
  if [ "$lang" = rust ] && command -v rustfilt >/dev/null; then
    sh_ "nm $obj | rustfilt"
  else
    sh_ "nm -C $obj"
  fi

  step "$lang: binding/visibility of defined functions and objects"
  sh_ "readelf -sW $obj | grep -E 'Num:|FUNC|OBJECT'"

  step "$lang: relocations (.rela.*), first lines"
  sh_ "readelf -rW $obj | head -25"

  step "$lang: disassembly together with relocations"
  sh_ "objdump -dr -M intel --no-show-raw-insn -C $obj | head -50"

  if readelf -SW "$obj" | grep -q '\.debug_info'; then
    step "$lang: DWARF debug information"
    sh_ "readelf -SW $obj | grep debug_"
    sh_ "readelf --debug-dump=info $obj | head -30"
  fi
done

echo; echo "${B}Итог: определённые внешние символы по языкам${R}"
for lang in $LANGS; do
  obj=build/$lang/$MODE/demo.o
  [ -f "$obj" ] && { echo "${D}-- $lang${R}"; nm -g --defined-only "$obj"; }
done
