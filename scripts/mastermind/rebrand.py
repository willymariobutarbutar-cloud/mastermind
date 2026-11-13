"""Rebrand user-visible 'DeepTutor' text to 'Mastermind' in a DeepTutor checkout.

Technical identifiers are left alone:
  - 'OpenDeepTutor' (desktop user-agent), 'HKUDS/DeepTutor' (repo refs),
    'DeepTutor_xxx' (file names), lowercase 'deeptutor' (packages, keys, paths).
i18n JSON: values are rebranded; keys keep the original and gain a rebranded
duplicate, so both renamed code keys and backend-sent original keys resolve.

Usage: python rebrand.py <repo root> [--dry-run]
"""
import json
import re
import sys
from pathlib import Path

NEW = "Mastermind"
WORD = re.compile(r"(?<![A-Za-z0-9/_.\-])DeepTutor(?![A-Za-z0-9_])")
OPEN_PREFIX = re.compile(r"\bOpen DeepTutor\b")

WEB_DIRS = ["app", "components", "features", "context", "hooks", "lib", "shared", "i18n", "types"]
WEB_SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".mjs"}
PROMPT_SUFFIXES = {".yaml", ".yml", ".md", ".j2", ".txt"}
# Terminal-facing messages (launcher, banner, doctor, CLI help).
CLI_DIRS = ["deeptutor_cli", "deeptutor/runtime"]


def rebrand_text(text: str) -> str:
    return WORD.sub(NEW, OPEN_PREFIX.sub(NEW, text))


def rebrand_json_tree(node):
    if isinstance(node, dict):
        out = {}
        for key, value in node.items():
            new_value = rebrand_json_tree(value)
            out[key] = new_value
            new_key = rebrand_text(key)
            if new_key != key and new_key not in node:
                out[new_key] = new_value
        return out
    if isinstance(node, str):
        return rebrand_text(node)
    return node


def text_targets(root: Path):
    web = root / "web"
    for d in WEB_DIRS:
        for p in (web / d).rglob("*"):
            if p.is_file() and p.suffix in WEB_SUFFIXES and "node_modules" not in p.parts:
                yield p
    for p in (root / "deeptutor").rglob("*"):
        if p.is_file() and p.suffix in PROMPT_SUFFIXES and "prompts" in p.parts:
            yield p
    for d in CLI_DIRS:
        for p in (root / d).rglob("*.py"):
            if p.is_file():
                yield p


def main(root: Path, dry: bool) -> None:
    changed = 0
    for p in text_targets(root):
        old = p.read_text(encoding="utf-8")
        new = rebrand_text(old)
        if new != old:
            changed += 1
            if not dry:
                p.write_text(new, encoding="utf-8")
    for p in sorted((root / "web" / "locales").glob("*/*.json")):
        old = p.read_text(encoding="utf-8")
        data = json.loads(old)
        new_data = rebrand_json_tree(data)
        if new_data != data:
            changed += 1
            if not dry:
                p.write_text(json.dumps(new_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{'would change' if dry else 'changed'} {changed} files")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    if len(args) != 1:
        raise SystemExit(__doc__)
    main(Path(args[0]).resolve(), "--dry-run" in sys.argv)
