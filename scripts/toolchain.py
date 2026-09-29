#!/usr/bin/env python3
"""How each language turns source code into an ELF object file.

All comparison parameters are collected here so they are in one place and appear in the report.
Environment variables: CXX, RUSTC, ZIG (compiler paths),
EXTRA_CXXFLAGS, EXTRA_RUSTFLAGS, EXTRA_ZIGFLAGS (additional flags, space-separated).
"""
import os
import shlex
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANGS = ("cpp", "rust", "zig")
LANG_NAME = {"cpp": "C++", "rust": "Rust", "zig": "Zig"}
EXT = {"cpp": "cpp", "rust": "rs", "zig": "zig"}
PROGS = ("demo", "generics", "strings", "errors", "cabi")

# Modes: semantically comparable optimization and debug information settings.
MODES = {
    "O0g": dict(cpp=["-O0", "-g"], rust_opt="0", rust_dbg="2", zig_opt="Debug", zig_strip=False),
    "O2":  dict(cpp=["-O2"],       rust_opt="2", rust_dbg="0", zig_opt="ReleaseFast", zig_strip=True),
    "O2g": dict(cpp=["-O2", "-g"], rust_opt="2", rust_dbg="2", zig_opt="ReleaseFast", zig_strip=False),
    "Os":  dict(cpp=["-Os"],       rust_opt="s", rust_dbg="0", zig_opt="ReleaseSmall", zig_strip=True),
}


def _extra(name):
    return shlex.split(os.environ.get(name, ""))


def tool(lang):
    """Compiler path, or None if unavailable."""
    if lang == "cpp":
        return os.environ.get("CXX") or shutil.which("clang++") or shutil.which("g++")
    if lang == "rust":
        return os.environ.get("RUSTC") or shutil.which("rustc")
    if lang == "zig":
        return os.environ.get("ZIG") or shutil.which("zig")
    raise ValueError(lang)


def source(lang, prog):
    return ROOT / "src" / lang / f"{prog}.{EXT[lang]}"


def compile_cmd(lang, src, out, mode, extra=None, cache=None):
    """Compilation command for a single source file into an object file.

    extra  : additional flags (for example, path remapping for reproducibility checks)
    cache  : Zig cache directory (separate for each run so the measurement is “cold”)
    """
    m = MODES[mode]
    extra = list(extra or [])
    exe = tool(lang)
    src, out = str(src), str(out)
    if lang == "cpp":
        return [exe, "-std=c++20", "-c", "-fPIC", "-march=x86-64", *m["cpp"],
                *_extra("EXTRA_CXXFLAGS"), *extra, src, "-o", out]
    if lang == "rust":
        crate = "obj_" + Path(src).stem
        return [exe, "--edition", "2021", "--crate-type=lib", "--crate-name", crate,
                "--emit=obj", "-C", f"opt-level={m['rust_opt']}",
                "-C", f"debuginfo={m['rust_dbg']}",
                "-C", "codegen-units=1",          # один .o на крейт
                "-C", "relocation-model=pic", "-C", "target-cpu=x86-64",
                *_extra("EXTRA_RUSTFLAGS"), *extra, "-o", out, src]
    if lang == "zig":
        cache = cache or str(ROOT / "build" / ".zig-cache")
        return [exe, "build-obj", src, "-O", m["zig_opt"],
                "-target", "x86_64-linux-gnu", "-mcpu", "baseline", "-fPIC",
                "-fllvm",                            # тот же LLVM-бэкенд, что у clang и rustc
                "-fstrip" if m["zig_strip"] else "-fno-strip",
                "--cache-dir", os.path.join(cache, "local"),
                "--global-cache-dir", os.path.join(cache, "global"),
                f"-femit-bin={out}", *_extra("EXTRA_ZIGFLAGS"), *extra]
    raise ValueError(lang)


def _first_line(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return (r.stdout or r.stderr).strip().splitlines()[0]
    except Exception as e:  # noqa: BLE001
        return f"n/a ({e})"


def versions():
    """Tool versions for the report."""
    v = {}
    for lang in LANGS:
        t = tool(lang)
        if not t:
            v[lang] = "not found"
        elif lang == "zig":
            v[lang] = _first_line([t, "version"])
        else:
            v[lang] = _first_line([t, "--version"])
    v["readelf"] = _first_line(["readelf", "--version"])
    return v
