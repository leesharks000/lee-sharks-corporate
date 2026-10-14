#!/usr/bin/env python3
"""sync_fraction.py — Ask Rex Fraction on every page of this site, once (2026-10-14).

The panel is the Mandala Oracle's embed/fraction.js: the oracle's own endpoint in mode 'fraction'. The same file sits
in spxi-dev and lee-sharks-corporate (semanticeconomy.org); run it after any page-writing step.

THE RULE. Every tracked .html page carries the tag exactly once, immediately before its last </body>. A redirect stub
(meta refresh) and a backup page (*_backup.html) are left alone; a page with no </body> is reported and left alone; a
page carrying the tag more than once is reduced to one. Insertion only. Idempotent.

  python3 scripts/sync_fraction.py           # write
  python3 scripts/sync_fraction.py --check   # report only; exit 0 always (laws record, they do not prevent)
"""
import pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = "https://www.themandalaoracle.com/embed/fraction.js"
TAG = f'<script src="{SRC}" defer></script>'
TAG_RE = re.compile(r'[ \t]*<script\b[^>]*\bsrc="https://www\.themandalaoracle\.com/embed/fraction\.js"[^>]*>\s*</script>[ \t]*\n?')
REFRESH_RE = re.compile(r'<meta[^>]+http-equiv=["\']?refresh', re.I)
BODY_END_RE = re.compile(r'</body\s*>', re.I)


def pages():
    out = subprocess.check_output(["git", "-c", "core.quotepath=off", "ls-files", "-z", "*.html"], cwd=ROOT)
    for f in out.decode("utf-8").split("\0"):
        if f and not f.endswith("_backup.html") and "/node_modules/" not in f:
            yield f


def ensure(html):
    if REFRESH_RE.search(html):
        return html, "redirect"
    n = len(TAG_RE.findall(html))
    if n == 1:
        return html, "present"
    if n > 1:
        first = TAG_RE.search(html)
        return html[:first.end()] + TAG_RE.sub("", html[first.end():]), "deduped"
    ends = list(BODY_END_RE.finditer(html))
    if not ends:
        return html, "no-body"
    i = ends[-1].start()
    return html[:i] + TAG + "\n" + html[i:], "added"


def main():
    check = "--check" in sys.argv
    tally, nobody = {}, []
    for f in pages():
        p = ROOT / f
        s = p.read_text(encoding="utf-8", errors="surrogateescape")
        new, act = ensure(s)
        tally[act] = tally.get(act, 0) + 1
        if act == "no-body":
            nobody.append(f)
        if new != s and not check:
            p.write_text(new, encoding="utf-8", errors="surrogateescape")
    print(f"sync_fraction ({'check' if check else 'write'}): " + ", ".join(f"{k} {v}" for k, v in sorted(tally.items())))
    for f in nobody:
        print("  no-body:", f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
