#!/usr/bin/env python3
"""Fetch public, non-fork TwitchCaptain repos and write projects.json."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ORG = "TwitchCaptain"
SITE_HOST = "https://twitchcaptain.com"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "projects.json"
API = "https://api.github.com"

EMOJI_PREFIX = re.compile(r"^[\U0001F300-\U0001FAFF\u2600-\u27BF\uFE0F\u200D\s]+")


def api_get(url: str, token: str | None) -> object:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "twitchcaptain-site-sync",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def list_repos(token: str | None) -> list[dict]:
    repos: list[dict] = []
    page = 1
    while True:
        url = (
            f"{API}/orgs/{ORG}/repos?type=public&per_page=100"
            f"&sort=updated&direction=desc&page={page}"
        )
        batch = api_get(url, token)
        if not isinstance(batch, list) or not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return repos


def clean_description(text: str | None) -> str:
    value = EMOJI_PREFIX.sub("", (text or "").strip()).strip()
    return value or "No description provided."


def pages_url_for(repo: dict) -> str | None:
    if not repo.get("has_pages"):
        return None
    homepage = (repo.get("homepage") or "").strip()
    if homepage:
        return homepage if homepage.endswith("/") else f"{homepage}/"
    return f"{SITE_HOST}/{repo['name']}/"


def to_project(repo: dict) -> dict | None:
    name = repo.get("name") or ""
    if repo.get("fork") or repo.get("archived"):
        return None
    if name.endswith(".github.io") or name == ".github":
        return None
    if repo.get("private"):
        return None

    return {
        "name": name,
        "description": clean_description(repo.get("description")),
        "url": repo.get("html_url"),
        "homepage": (repo.get("homepage") or "").strip() or None,
        "pages_url": pages_url_for(repo),
        "language": repo.get("language"),
        "topics": repo.get("topics") or [],
        "pushed_at": repo.get("pushed_at"),
        "stargazers_count": repo.get("stargazers_count", 0),
    }


def main() -> int:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    try:
        repos = list_repos(token)
    except urllib.error.HTTPError as exc:
        print(f"GitHub API error: {exc}", file=sys.stderr)
        return 1

    projects = [p for p in (to_project(r) for r in repos) if p]
    # Stable: most recently pushed first, then name.
    projects.sort(key=lambda p: (p.get("pushed_at") or "", p["name"]), reverse=True)

    payload = json.dumps(projects, indent=2, ensure_ascii=False) + "\n"
    previous = OUT.read_text(encoding="utf-8") if OUT.exists() else None
    if previous == payload:
        print(f"No changes ({len(projects)} projects).")
        return 0

    OUT.write_text(payload, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} with {len(projects)} projects.")
    for project in projects:
        pages = f" pages={project['pages_url']}" if project.get("pages_url") else ""
        print(f"  - {project['name']}{pages}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
