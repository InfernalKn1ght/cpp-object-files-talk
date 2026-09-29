#!/usr/bin/env python3
"""Check reproducibility of object file builds.

The same source is built twice: in different directories and at different times.
Variants:  plain — without special flags;  remap — with path prefix remapping
(-ffile-prefix-map for C++, --remap-path-prefix for Rust; Zig has no such flag here).
sha256 hashes are compared. O2g mode (with -g), because absolute paths end up in DWARF.

  python3 scripts/repro.py [--langs cpp,rust,zig] [--progs demo,errors]
"""
import argparse
import csv
import hashlib
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import toolchain as tc

MODE = "O2g"


def remap_flags(lang, root):
    if lang == "cpp":
        return [f"-ffile-prefix-map={root}=/src"]
    if lang == "rust":
        return [f"--remap-path-prefix={root}=/src"]
    return []


def build(lang, prog, tag, variant, tmp):
    root = Path(tmp) / tag / "project"
    shutil.copytree(tc.ROOT / "src" / lang, root / "src" / lang)
    out = root / "out.o"
    extra = remap_flags(lang, root) if variant == "remap" else []
    src = root / "src" / lang / f"{prog}.{tc.EXT[lang]}"
    cmd = tc.compile_cmd(lang, src, out, MODE, extra=extra, cache=str(root / ".zig-cache"))
    r = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-800:])
    return out


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def first_diff_hint(a, b):
    """Hint: which lines of readelf --debug-dump=info output differ between the files."""
    def dump(p):
        return subprocess.run(["readelf", "--debug-dump=info", str(p)],
                              capture_output=True, text=True).stdout.splitlines()
    la, lb = dump(a), dump(b)
    for x, y in zip(la, lb):
        if x != y:
            return f"{x.strip()[:60]}  |  {y.strip()[:60]}"
    return "differences outside .debug_info"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--langs", default=",".join(tc.LANGS))
    ap.add_argument("--progs", default="demo,errors")
    ap.add_argument("--outdir", default=str(tc.ROOT / "results"))
    a = ap.parse_args()

    rows = []
    print(f"{'lang':5} {'prog':9} {'variant':7} {'identical':9}  hint")
    for lang in a.langs.split(","):
        if not tc.tool(lang):
            print(f"{lang:5} skipped: compiler not found")
            continue
        for prog in a.progs.split(","):
            for variant in ("plain", "remap"):
                with tempfile.TemporaryDirectory() as tmp:
                    try:
                        o1 = build(lang, prog, "a_short", variant, tmp)
                        time.sleep(1.1)                     # другое время сборки
                        o2 = build(lang, prog, "b_longer_dir_name", variant, tmp)
                    except RuntimeError as e:
                        print(f"{lang:5} {prog:9} {variant:7} BUILD ERROR\n{e}")
                        continue
                    same = sha(o1) == sha(o2)
                    hint = "" if same else first_diff_hint(o1, o2)
                    rows.append(dict(lang=lang, prog=prog, variant=variant,
                                     identical=int(same), sha_a=sha(o1)[:16], sha_b=sha(o2)[:16]))
                    print(f"{lang:5} {prog:9} {variant:7} {'yes' if same else 'NO':9}  {hint}")
    out = Path(a.outdir)
    out.mkdir(exist_ok=True)
    with open(out / "repro.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["lang", "prog", "variant", "identical", "sha_a", "sha_b"],
                           lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"\nwritten: {out}/repro.csv")


if __name__ == "__main__":
    main()
