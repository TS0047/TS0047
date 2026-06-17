import os
import re
import requests
from datetime import datetime, timezone
from collections import defaultdict

OWNER = "TS0047"
REPO = "neetcode-submissions"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"}

def get_tree():
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/git/trees/main?recursive=1"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json().get("tree", [])

def parse_problems(tree):
    categories = defaultdict(set)
    for item in tree:
        path = item["path"]
        parts = path.split("/")
        if len(parts) >= 2 and item["type"] == "blob":
            category = parts[0]
            problem = parts[1]
            categories[category].add(problem)
    return categories

def category_emoji(name):
    name_lower = name.lower()
    if "array" in name_lower or "hash" in name_lower:
        return "🗂️"
    if "pointer" in name_lower:
        return "👉"
    if "sliding" in name_lower or "window" in name_lower:
        return "🪟"
    if "stack" in name_lower:
        return "📚"
    if "binary" in name_lower:
        return "🔍"
    if "link" in name_lower:
        return "🔗"
    if "tree" in name_lower:
        return "🌳"
    if "graph" in name_lower:
        return "🕸️"
    if "dp" in name_lower or "dynamic" in name_lower:
        return "🧮"
    if "heap" in name_lower or "priority" in name_lower:
        return "⛏️"
    if "backtrack" in name_lower:
        return "↩️"
    if "interval" in name_lower:
        return "📏"
    if "greedy" in name_lower:
        return "💰"
    if "bit" in name_lower:
        return "⚡"
    if "math" in name_lower:
        return "➗"
    return "💡"

def build_markdown(categories):
    filtered = {k: v for k, v in categories.items() if not k.startswith(".")}
    total = sum(len(v) for v in filtered.values())
    updated = datetime.now(timezone.utc).strftime("%b %d, %Y")

    rows = ""
    for cat, problems in sorted(filtered.items(), key=lambda x: -len(x[1])):
        emoji = category_emoji(cat)
        short = cat.replace("Data Structures & Algorithms", "DS&A")
        rows += f"| {emoji} {short} | `{len(problems)}` |\n"

    bar_filled = min(int((total / 150) * 20), 20)
    bar = "█" * bar_filled + "░" * (20 - bar_filled)

    md = f"""<!-- NEETCODE-START -->
<div align="center">

## 🧠 NeetCode Grind

![Problems](https://img.shields.io/badge/Solved-{total}_problems-brightgreen?style=for-the-badge&logo=leetcode&logoColor=white)&nbsp;
![Language](https://img.shields.io/badge/Language-Python-3776AB?style=for-the-badge&logo=python&logoColor=white)&nbsp;
![Updated](https://img.shields.io/badge/Updated-{updated.replace(" ", "_")}-blue?style=for-the-badge)

```
Progress  [{bar}]  {total}/150+
```

| Category | Solved |
|:---------|:------:|
{rows}
> 🔄 Auto-updated daily · [View repo](https://github.com/{OWNER}/{REPO})

</div>
<!-- NEETCODE-END -->"""
    return md

def update_readme(new_block):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r"<!-- NEETCODE-START -->.*?<!-- NEETCODE-END -->"
    if re.search(pattern, content, re.DOTALL):
        updated = re.sub(pattern, new_block, content, flags=re.DOTALL)
    else:
        updated = content + "\n\n" + new_block

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated)
    print("README.md updated.")

if __name__ == "__main__":
    tree = get_tree()
    categories = parse_problems(tree)
    block = build_markdown(categories)
    update_readme(block)
    print(block)
