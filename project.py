#!/usr/bin/env python3
"""Turn on the platform packs a project needs, for this machine only.

Detects packs from the project's files, links their skills into the project's
.claude/skills, .agents/skills and .cursor/skills, and enables their Claude Code
plugins in .claude/settings.local.json. Everything it creates is listed in
.git/info/exclude, so the project's git status stays clean. Safe to rerun.

Usage: ./project.py [PROJECT_DIR] [--add PACK] [--remove PACK] [--dry-run]
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
PACKS = REPO / "packs"
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", ".turbo", ".expo", "ios", "android", ".vercel"}
MAX_DEPTH = 4
EXCLUDE_START = "# agent-skills packs (managed by agent-skills/project.py)"
EXCLUDE_END = "# end agent-skills packs"
SELECTION_FILE = ".agent-packs"


def check_inside(root, path):
    """Stop if a path we read or write is a symlink, or resolves outside the project.

    A cloned project could plant .claude/settings.local.json or .claude/skills as a
    symlink to a file elsewhere, which would make this script write there.
    """
    current = root
    for part in path.relative_to(root).parts:
        current = current / part
        if current.is_symlink():
            sys.exit(f"Refusing to use {current}: it is a symlink. Remove it and rerun.")
    if not os.path.realpath(path).startswith(os.path.realpath(root) + os.sep):
        sys.exit(f"Refusing to use {path}: it resolves outside {root}.")
    return path


def load_packs():
    packs = {}
    for manifest in sorted(PACKS.glob("*/pack.json")):
        data = json.loads(manifest.read_text())
        skills_dir = manifest.parent / "skills"
        data["skills"] = sorted(p for p in skills_dir.iterdir() if (p / "SKILL.md").exists()) if skills_dir.is_dir() else []
        packs[manifest.parent.name] = data
    return packs


def project_files(root):
    """Relative paths of files up to MAX_DEPTH, skipping build and vendor folders."""
    for dirpath, dirnames, filenames in os.walk(root):
        rel = Path(dirpath).relative_to(root)
        depth = 0 if rel == Path(".") else len(rel.parts)
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not (depth >= MAX_DEPTH)]
        # .vercel/project.json is a detection target even though .vercel is skipped for walking.
        if depth == 0 and (root / ".vercel" / "project.json").exists():
            yield Path(".vercel/project.json")
        for name in filenames:
            yield rel / name


def dependencies(root, files):
    deps = set()
    for path in files:
        if path.name != "package.json":
            continue
        try:
            data = json.loads((root / path).read_text())
        except (OSError, json.JSONDecodeError):
            continue
        for key in ("dependencies", "devDependencies", "peerDependencies"):
            deps.update((data.get(key) or {}).keys())
    return deps


def detect(root, packs):
    files = list(project_files(root))
    as_posix = {p.as_posix() for p in files}
    deps = dependencies(root, files)
    found = set()
    for name, pack in packs.items():
        for rule in pack.get("detect", []):
            if "dependency" in rule and rule["dependency"] in deps:
                found.add(name)
            target = rule.get("file")
            if target and any(p == target or p.endswith("/" + target) for p in as_posix):
                found.add(name)
    return found


def read_selection(root):
    added, removed = set(), set()
    path = check_inside(root, root / SELECTION_FILE)
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            (removed.add(line[1:]) if line.startswith("-") else added.add(line))
    return added, removed


def write_selection(root, added, removed, dry):
    lines = ["# Packs for this project on this machine. A line 'name' adds a pack, '-name' turns off a detected one."]
    lines += sorted(added) + sorted("-" + r for r in removed)
    if not dry:
        (root / SELECTION_FILE).write_text("\n".join(lines) + "\n")


def link_skills(root, active, packs, dry):
    dest_dirs = [root / ".claude" / "skills", root / ".agents" / "skills"]
    if (Path.home() / ".cursor").is_dir():
        dest_dirs.append(root / ".cursor" / "skills")
    wanted = {skill.name: skill for name in active for skill in packs[name]["skills"]}
    created = []
    for dest_dir in dest_dirs:
        check_inside(root, dest_dir)
        # Remove links to pack skills that are no longer active.
        if dest_dir.is_dir():
            for entry in dest_dir.iterdir():
                if entry.is_symlink() and str(PACKS) in os.readlink(entry) and entry.name not in wanted:
                    print(f"  remove {entry.relative_to(root)}")
                    if not dry:
                        entry.unlink()
        for name, src in wanted.items():
            dest = dest_dir / name
            if dest.is_symlink() and os.readlink(dest) == str(src):
                created.append(dest)
                continue
            if dest.exists() or dest.is_symlink():
                print(f"  skip {dest.relative_to(root)}: the project already has its own copy")
                continue
            print(f"  link {dest.relative_to(root)}")
            if not dry:
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest.symlink_to(src)
            created.append(dest)
    return created


def update_plugins(root, active, packs, dry):
    path = check_inside(root, root / ".claude" / "settings.local.json")
    settings = json.loads(path.read_text()) if path.exists() else {}
    enabled = settings.get("enabledPlugins", {})
    before = dict(enabled)
    for name, pack in packs.items():
        for plugin in pack.get("plugins", {}):
            if name in active:
                enabled[plugin] = True
            else:
                enabled.pop(plugin, None)
    if enabled == before:
        return path.exists()
    for plugin in sorted(set(enabled) | set(before)):
        if enabled.get(plugin) != before.get(plugin):
            print(f"  plugin {plugin}: {'on' if enabled.get(plugin) else 'off'}")
    if enabled:
        settings["enabledPlugins"] = enabled
    else:
        settings.pop("enabledPlugins", None)
    if not dry:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(settings, indent=2) + "\n")
    return True


def update_exclude(root, paths, dry):
    out = subprocess.run(["git", "-C", str(root), "rev-parse", "--git-path", "info/exclude"], capture_output=True, text=True)
    if out.returncode != 0:
        print("  not a git repository, so nothing was added to .git/info/exclude")
        return
    exclude = Path(out.stdout.strip())
    if not exclude.is_absolute():
        exclude = root / exclude
    if exclude.is_symlink():
        sys.exit(f"Refusing to use {exclude}: it is a symlink. Remove it and rerun.")
    text = exclude.read_text() if exclude.exists() else ""
    if EXCLUDE_START in text:
        head, _, rest = text.partition(EXCLUDE_START)
        _, _, tail = rest.partition(EXCLUDE_END)
        text = head.rstrip("\n") + ("\n" if head.strip() else "") + tail.lstrip("\n")
    block = [EXCLUDE_START] + sorted("/" + p.relative_to(root).as_posix() for p in paths) + [EXCLUDE_END]
    text = text.rstrip("\n") + ("\n" if text.strip() else "") + "\n".join(block) + "\n"
    if not dry:
        exclude.parent.mkdir(parents=True, exist_ok=True)
        exclude.write_text(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("project", nargs="?", default=".")
    parser.add_argument("--add", action="append", default=[], metavar="PACK")
    parser.add_argument("--remove", action="append", default=[], metavar="PACK")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.project).resolve()
    top = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if top.returncode == 0:
        root = Path(top.stdout.strip())
    if root == REPO:
        sys.exit("Run this against a project, not the agent-skills repo itself.")

    packs = load_packs()
    for name in args.add + args.remove:
        if name not in packs:
            sys.exit(f"Unknown pack '{name}'. Packs: {', '.join(packs)}")

    added, removed = read_selection(root)
    added = (added | set(args.add)) - set(args.remove)
    removed = (removed | set(args.remove)) - set(args.add)
    detected = detect(root, packs)
    active = (detected | added) - removed

    print(f"{root}")
    print(f"  detected: {', '.join(sorted(detected)) or 'none'}")
    print(f"  active:   {', '.join(sorted(active)) or 'none'}")

    managed = link_skills(root, active, packs, args.dry_run)
    if update_plugins(root, active, packs, args.dry_run):
        managed.append(root / ".claude" / "settings.local.json")
    if added or removed:
        write_selection(root, added, removed, args.dry_run)
        managed.append(root / SELECTION_FILE)
    update_exclude(root, managed, args.dry_run)
    print("Dry run only. Nothing changed." if args.dry_run else "Done.")


if __name__ == "__main__":
    main()
