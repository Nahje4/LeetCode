import json
import re
import sys
import time
import urllib.request
from pathlib import Path

LEETCODE_USER = "Nahje"
ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
CACHE = ROOT / "scripts" / "leetcode_cache.json"
DIFF_DIRS = ("Easy", "Medium", "Hard")
DIR_RE = re.compile(r"^(\d+)\.(.+)$")

LANGS = {
    ".c": ("c", "C"),
    ".cc": ("cpp", "C++"),
    ".cpp": ("cpp", "C++"),
    ".rs": ("rust", "Rust"),
    ".py": ("python", "Python"),
    ".go": ("go", "Go"),
    ".java": ("java", "Java"),
    ".ts": ("ts", "TypeScript"),
    ".js": ("js", "JavaScript"),
    ".ml": ("ocaml", "OCaml"),
}
DIFF_LEVEL = {"Easy": 1, "Medium": 2, "Hard": 3}
DIFF_COLOR = {"Easy": "00B8A3", "Medium": "FFC01E", "Hard": "EF4743", "All": "FFA116"}

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (readme-bot; +https://github.com/Nahje4/LeetCode)",
    "Referer": "https://leetcode.com",
}


def http_json(url, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def graphql(query, variables):
    return http_json("https://leetcode.com/graphql",
                     {"query": query, "variables": variables})["data"]


def fetch_problem_index():
    """frontend id -> slug, for every problem (one request)."""
    try:
        data = http_json("https://leetcode.com/api/problems/all/")
        return {str(p["stat"]["frontend_question_id"]): p["stat"]["question__title_slug"]
                for p in data["stat_status_pairs"]}
    except Exception as e:
        print(f"warn: problem index unavailable ({e}); slugs guessed from folder names")
        return {}


def fetch_question(slug):
    q = graphql(
        "query q($s:String!){question(titleSlug:$s){questionFrontendId title "
        "titleSlug difficulty topicTags{name}}}", {"s": slug})["question"]
    if not q:
        raise ValueError(f"unknown slug {slug!r}")
    return {"id": q["questionFrontendId"], "title": q["title"], "slug": q["titleSlug"],
            "difficulty": q["difficulty"], "tags": [t["name"] for t in q["topicTags"]]}


def fetch_profile_stats():
    d = graphql(
        "query u($u:String!){allQuestionsCount{difficulty count} "
        "matchedUser(username:$u){submitStats{acSubmissionNum{difficulty count}}}}",
        {"u": LEETCODE_USER})
    total = {x["difficulty"]: x["count"] for x in d["allQuestionsCount"]}
    solved = {x["difficulty"]: x["count"]
              for x in d["matchedUser"]["submitStats"]["acSubmissionNum"]}
    return {k: (solved.get(k, 0), total.get(k, 0)) for k in ("Easy", "Medium", "Hard", "All")}


def guess_slug(name):
    s = name.replace("_", "-").lower()
    s = re.sub(r"[^a-z0-9-]", "", s)
    return re.sub(r"-+", "-", s).strip("-")


def read_complexity(files):
    time_c = space_c = None
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        time_c = time_c or _grab(r"time(?:\s+complexity)?", text)
        space_c = space_c or _grab(r"space(?:\s+complexity)?", text)
    return time_c, space_c


def _grab(label, text):
    m = re.search(rf"(?im)^\s*(?://|#|--|\*|/\*)\s*{label}\s*:\s*(O\(.*?\))\s*(?:\*/)?\s*$", text)
    return m.group(1) if m else None


def scan():
    problems = []
    for diff in DIFF_DIRS:
        base = ROOT / diff
        if not base.is_dir():
            continue
        for d in sorted(base.iterdir()):
            m = DIR_RE.match(d.name)
            if not d.is_dir() or not m:
                continue
            files = sorted((f for f in d.iterdir() if f.suffix in LANGS),
                           key=lambda f: list(LANGS).index(f.suffix))
            if files:
                problems.append({"id": m.group(1), "name": m.group(2),
                                 "folder_diff": diff, "dir": d, "files": files})
    return sorted(problems, key=lambda p: int(p["id"]))


def icon(lang_id, size=20):
    return f'<img src="https://skillicons.dev/icons?i={lang_id}" width="{size}"/>'


def difficulty_badge(diff):
    level = DIFF_LEVEL.get(diff)
    if not level:
        return diff
    bars = "%20".join(["%E2%96%B0"] * level + ["%E2%96%B1"] * (3 - level))
    return (f'<img src="https://img.shields.io/badge/{bars}-{DIFF_COLOR[diff]}'
            f'?style=flat-square" width="64" height="20" alt="{diff}" title="{diff}"/>')


def render_table(problems, cache):
    rows = ["| # | Problem | Difficulty | Pattern | Solution | Time | Space |",
            "|:--:|:--|:--:|:--|:--:|:--:|:--:|"]
    for p in problems:
        meta = cache.get(p["id"])
        title = meta["title"] if meta else p["name"].replace("_", " ")
        slug = meta["slug"] if meta else guess_slug(p["name"])
        diff = meta["difficulty"] if meta else p["folder_diff"]
        tags = ", ".join(meta["tags"][:3]) if meta else ""
        links, seen = [], set()
        for f in p["files"]:
            lang_id = LANGS[f.suffix][0]
            if lang_id in seen:
                continue
            seen.add(lang_id)
            links.append(f"[{icon(lang_id)}]({f.relative_to(ROOT).as_posix()})")
        t, s = read_complexity(p["files"])
        rows.append(
            f"| {p['id']} | [{title}](https://leetcode.com/problems/{slug}/) "
            f"| {difficulty_badge(diff)} | {tags} | {' '.join(links)} "
            f"| {f'`{t}`' if t else '—'} | {f'`{s}`' if s else '—'} |")
    return "\n".join(rows)


def render_stats(stats):
    out = []
    for k, label in (("Easy", "Easy"), ("Medium", "Medium"), ("Hard", "Hard"), ("All", "Total")):
        solved, total = stats[k]
        out.append(f'<img src="https://img.shields.io/badge/{label}-{solved}%20%2F%20{total}'
                   f'-{DIFF_COLOR[k]}?style=for-the-badge&labelColor=1A1A1A"/>')
    return "\n".join(out)


def render_langs(problems):
    ids = []
    for p in problems:
        for f in p["files"]:
            i = LANGS[f.suffix][0]
            if i not in ids:
                ids.append(i)
    order = [v[0] for v in LANGS.values()]
    ids.sort(key=order.index)
    names = " · ".join(dict.fromkeys(n for ext, (i, n) in LANGS.items() if i in ids))
    return f'<img src="https://skillicons.dev/icons?i={",".join(ids)}&theme=dark" alt="{names}"/>'


def replace_block(text, name, body):
    pat = re.compile(rf"(<!-- {name}:START -->).*?(<!-- {name}:END -->)", re.S)
    if not pat.search(text):
        print(f"warn: markers for {name} not found in README")
        return text
    return pat.sub(lambda m: f"{m.group(1)}\n{body}\n{m.group(2)}", text)


def main():
    problems = scan()
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}

    missing = [p for p in problems if p["id"] not in cache]
    if missing:
        index = fetch_problem_index()
        for p in missing:
            slug = index.get(p["id"]) or guess_slug(p["name"])
            try:
                cache[p["id"]] = fetch_question(slug)
                print(f"fetched #{p['id']} {slug}")
            except Exception as e:
                print(f"warn: #{p['id']} ({slug}) not fetched: {e}")
            time.sleep(0.5)
        CACHE.write_text(json.dumps(cache, indent=2, ensure_ascii=False, sort_keys=True) + "\n")

    text = README.read_text(encoding="utf-8")
    text = replace_block(text, "SOLUTIONS-TABLE", render_table(problems, cache))
    text = replace_block(text, "LANGS", render_langs(problems))
    try:
        text = replace_block(text, "STATS", render_stats(fetch_profile_stats()))
    except Exception as e:
        print(f"warn: profile stats not updated: {e}")
    README.write_text(text, encoding="utf-8")
    print(f"README updated: {len(problems)} problems")


if __name__ == "__main__":
    sys.exit(main())