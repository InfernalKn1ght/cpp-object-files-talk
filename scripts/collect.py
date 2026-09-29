#!/usr/bin/env python3
"""Build object files and collect metrics.

For each combination (language, program, mode):
  1. compiles the source into .o (measuring time and peak memory);
  2. analyzes .o with readelf: sections, symbols, relocations;
  3. appends rows to results/metrics.csv, sections.csv, relocs.csv.

Example:  python3 scripts/collect.py --runs 10
         python3 scripts/collect.py --langs cpp --progs demo --modes O0g,O2 --build-only
"""
import argparse
import csv
import os
import platform
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

import toolchain as tc

SEC_RE = re.compile(
    r"^\s*\[\s*(\d+)\]\s+(\S+)\s+(\S+)\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)"
    r"\s+([0-9a-f]+)\s+([A-Za-z]*)\s+(\d+)\s+(\d+)\s+(\d+)\s*$")
REL_HDR = re.compile(r"Relocation section '(.+?)' at offset")
REL_ROW = re.compile(r"^[0-9a-f]{8,16}\s+[0-9a-f]+\s+(R_\S+)")


# ---------------------------------------------------------------- ELF parsing
def readelf(args, path):
    r = subprocess.run(["readelf", "-W", *args, str(path)],
                       capture_output=True, text=True, check=True)
    return r.stdout


def parse_sections(path):
    secs = []
    for line in readelf(["-S"], path).splitlines():
        m = SEC_RE.match(line)
        if not m or int(m.group(1)) == 0:
            continue
        secs.append(dict(idx=int(m.group(1)), name=m.group(2), type=m.group(3),
                         size=int(m.group(6), 16), flags=m.group(8)))
    return secs


def sec_category(name):
    if name.startswith(".text"):
        return "text"
    if name.startswith(".rodata"):
        return "rodata"
    if name.startswith((".data", ".tdata")):
        return "data"
    if name.startswith((".bss", ".tbss")):
        return "bss"
    if name.startswith((".debug_", ".zdebug_")):
        return "debug"
    if name in (".eh_frame", ".gcc_except_table"):
        return "eh"
    if name in (".symtab", ".strtab", ".shstrtab"):
        return "symtab"
    if name.startswith((".rela", ".rel.")):
        return "reloc"
    return "other"


def parse_symbols(path):
    c = Counter()
    for line in readelf(["-s"], path).splitlines():
        p = line.split()
        if len(p) < 7 or not p[0].endswith(":") or not p[0][:-1].isdigit():
            continue
        if int(p[0][:-1]) == 0:          # null symbol
            continue
        typ, bind, vis, ndx = p[3], p[4], p[5], p[6]
        c["sym_total"] += 1
        c["sym_undef" if ndx == "UND" else "sym_def"] += 1
        c["sym_" + bind.lower()] += 1     # local / global / weak
        c["sym_t_" + typ.lower()] += 1    # func / object / tls / section / file / notype
        if vis == "HIDDEN":
            c["sym_hidden"] += 1
        if ndx != "UND" and bind in ("GLOBAL", "WEAK"):
            c["sym_def_exported"] += 1
    return c


def parse_relocs(path):
    """-> (Counter by type, Counter by code/debug/eh group)."""
    types, groups = Counter(), Counter()
    cur = None
    for line in readelf(["-r"], path).splitlines():
        h = REL_HDR.search(line)
        if h:
            cur = h.group(1)
            continue
        m = REL_ROW.match(line)
        if m and cur:
            types[m.group(1)] += 1
            if ".debug_" in cur:
                groups["debug"] += 1
            elif "eh_frame" in cur or "gcc_except_table" in cur:
                groups["eh"] += 1
            else:
                groups["code"] += 1
    return types, groups


# ---------------------------------------------------------------- compiler execution
def timed_run(cmd, cwd):
    """Returns (return code, wall-clock seconds, rusage, stderr). ru_maxrss includes child processes."""
    with tempfile.TemporaryFile() as err:
        t0 = time.perf_counter()
        p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.DEVNULL, stderr=err)
        _, status, ru = os.wait4(p.pid, 0)
        wall = time.perf_counter() - t0
        p.returncode = os.waitstatus_to_exitcode(status)
        err.seek(0)
        msg = err.read().decode(errors="replace")
    return p.returncode, wall, ru, msg


def compile_measured(lang, prog, mode, out, runs, warmup):
    """Compiles runs times (+warmup). Zig gets a fresh cache for each run."""
    src = tc.source(lang, prog)
    walls, cpus, rsss = [], [], []
    for i in range(warmup + runs):
        cache = tempfile.mkdtemp(prefix="zigcache-") if lang == "zig" else None
        try:
            cmd = tc.compile_cmd(lang, src, out, mode, cache=cache)
            rc, wall, ru, msg = timed_run(cmd, tc.ROOT)
        finally:
            if cache:
                shutil.rmtree(cache, ignore_errors=True)
        if rc != 0:
            return None, msg
        if i >= warmup:
            walls.append(wall * 1000)
            cpus.append((ru.ru_utime + ru.ru_stime) * 1000)
            rsss.append(ru.ru_maxrss)        # KB on Linux
    return dict(compile_ms_median=statistics.median(walls),
                compile_ms_stdev=statistics.stdev(walls) if len(walls) > 1 else 0.0,
                compile_cpu_ms=statistics.median(cpus),
                max_rss_kb=statistics.median(rsss), runs=runs), ""


# ---------------------------------------------------------------- metrics for one .o
def analyze(obj):
    secs = parse_sections(obj)
    cat = Counter()
    for s in secs:
        if s["type"] == "NOBITS":        # .bss does not occupy space in the file
            cat["bss_mem"] += s["size"]
            continue
        cat[sec_category(s["name"])] += s["size"]
    syms = parse_symbols(obj)
    rtypes, rgroups = parse_relocs(obj)
    row = dict(
        obj_bytes=os.path.getsize(obj),
        sec_count=len(secs),
        sec_text=cat["text"], sec_data=cat["data"], sec_rodata=cat["rodata"],
        sec_debug=cat["debug"], sec_eh=cat["eh"], sec_symtab=cat["symtab"],
        sec_reloc=cat["reloc"], sec_other=cat["other"], bss_mem=cat["bss_mem"],
        n_groups=sum(1 for s in secs if s["type"] == "GROUP"),
        n_text_sections=sum(1 for s in secs if s["name"].startswith(".text")),
        rel_total=sum(rtypes.values()), rel_code=rgroups["code"],
        rel_debug=rgroups["debug"], rel_eh=rgroups["eh"],
    )
    for k in ("sym_total", "sym_def", "sym_undef", "sym_local", "sym_global", "sym_weak",
              "sym_hidden", "sym_def_exported", "sym_t_func", "sym_t_object", "sym_t_tls",
              "sym_t_section", "sym_t_file", "sym_t_notype"):
        row[k] = syms[k]
    return row, secs, rtypes


METRIC_FIELDS = [
    "lang", "prog", "mode", "obj_bytes", "sec_count", "sec_text", "sec_data", "sec_rodata",
    "sec_debug", "sec_eh", "sec_symtab", "sec_reloc", "sec_other", "bss_mem",
    "n_groups", "n_text_sections", "rel_total", "rel_code", "rel_debug", "rel_eh",
    "sym_total", "sym_def", "sym_undef", "sym_local", "sym_global", "sym_weak", "sym_hidden",
    "sym_def_exported", "sym_t_func", "sym_t_object", "sym_t_tls", "sym_t_section",
    "sym_t_file", "sym_t_notype",
    "compile_ms_median", "compile_ms_stdev", "compile_cpu_ms", "max_rss_kb", "runs",
]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--langs", default=",".join(tc.LANGS))
    ap.add_argument("--progs", default=",".join(tc.PROGS))
    ap.add_argument("--modes", default=",".join(tc.MODES))
    ap.add_argument("--runs", type=int, default=5, help="number of compilation measurements (use 10+ for final results)")
    ap.add_argument("--warmup", type=int, default=1)
    ap.add_argument("--build-only", action="store_true", help="build .o only, without measurements")
    ap.add_argument("--builddir", default=str(tc.ROOT / "build"))
    ap.add_argument("--outdir", default=str(tc.ROOT / "results"))
    a = ap.parse_args()

    if platform.machine() != "x86_64" or platform.system() != "Linux":
        print("WARNING: comparison is designed for x86-64 Linux (ELF); "
              f"здесь {platform.system()}/{platform.machine()}", file=sys.stderr)

    builddir, outdir = Path(a.builddir), Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    langs = [l for l in a.langs.split(",") if l]
    progs = [p for p in a.progs.split(",") if p]
    modes = [m for m in a.modes.split(",") if m]

    avail = []
    for l in langs:
        if tc.tool(l):
            avail.append(l)
        else:
            print(f"skipping {l}: compiler not found", file=sys.stderr)

    rows, sec_rows, rel_rows, failures = [], [], [], 0
    for lang in avail:
        for mode in modes:
            for prog in progs:
                out = builddir / lang / mode / f"{prog}.o"
                out.parent.mkdir(parents=True, exist_ok=True)
                tag = f"{lang}/{mode}/{prog}"
                if a.build_only:
                    cache = tempfile.mkdtemp(prefix="zigcache-") if lang == "zig" else None
                    rc, _, _, msg = timed_run(tc.compile_cmd(lang, tc.source(lang, prog), out, mode,
                                                             cache=cache), tc.ROOT)
                    if cache:
                        shutil.rmtree(cache, ignore_errors=True)
                    if rc:
                        failures += 1
                        print(f"[FAIL] {tag}\n{msg[-1500:]}", file=sys.stderr)
                    else:
                        print(f"[ok]   {tag}")
                    continue
                timing, msg = compile_measured(lang, prog, mode, out, a.runs, a.warmup)
                if timing is None:
                    failures += 1
                    print(f"[FAIL] {tag}\n{msg[-1500:]}", file=sys.stderr)
                    continue
                row, secs, rtypes = analyze(out)
                row.update(timing, lang=lang, prog=prog, mode=mode)
                rows.append(row)
                for s in secs:
                    sec_rows.append(dict(lang=lang, prog=prog, mode=mode, section=s["name"],
                                         size=s["size"], type=s["type"], flags=s["flags"]))
                for t, n in sorted(rtypes.items()):
                    rel_rows.append(dict(lang=lang, prog=prog, mode=mode, type=t, count=n))
                print(f"[ok]   {tag}: {row['obj_bytes']} B, {row['compile_ms_median']:.0f} ms")

    if not a.build_only:
        def dump(name, fields, data):
            with open(outdir / name, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
                w.writeheader()
                w.writerows(data)
        dump("metrics.csv", METRIC_FIELDS, rows)
        dump("sections.csv", ["lang", "prog", "mode", "section", "size", "type", "flags"], sec_rows)
        dump("relocs.csv", ["lang", "prog", "mode", "type", "count"], rel_rows)
        with open(outdir / "versions.txt", "w") as f:
            for k, v in tc.versions().items():
                f.write(f"{k}: {v}\n")
            f.write(f"platform: {platform.platform()}\nmachine: {platform.machine()}\n")
        print(f"\nwritten: {outdir}/metrics.csv, sections.csv, relocs.csv, versions.txt")
    if failures:
        print(f"compilation errors: {failures}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
