#!/usr/bin/env python3
import json
import os
import sys
import urllib.request

MARKER = "<!-- sssp2504-governance-comment -->"


def env(name, default=None):
    v = os.environ.get(name, default)
    if v is None:
        raise SystemExit(f"Missing required env: {name}")
    return v


def gh_request(method, url, token, data=None):
    req = urllib.request.Request(url=url, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    payload = None
    if data is not None:
        payload = json.dumps(data).encode("utf-8")
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, data=payload) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body) if body else None


def main():
    token = env("GITHUB_TOKEN")
    repo = env("GITHUB_REPOSITORY")
    pr_number = env("PR_NUMBER")
    dry_run = os.environ.get("PR_COMMENT_PUBLISH", "0") != "1"

    body_path = os.environ.get("PR_COMMENT_BODY_FILE", "reports/sssp2504-governance-pr-comment.md")
    if not os.path.exists(body_path):
        raise SystemExit(f"Comment body file not found: {body_path}")

    with open(body_path, "r", encoding="utf-8") as f:
        body = f.read().strip()

    full_body = f"{MARKER}\n{body}\n"

    base = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"

    if dry_run:
        print("DRY_RUN: would upsert PR comment")
        print(f"repo={repo} pr={pr_number} body_file={body_path}")
        return

    comments = gh_request("GET", base, token)
    existing = None
    for c in comments or []:
        if isinstance(c, dict) and MARKER in (c.get("body") or ""):
            existing = c
            break

    if existing:
        cid = existing["id"]
        url = f"https://api.github.com/repos/{repo}/issues/comments/{cid}"
        gh_request("PATCH", url, token, {"body": full_body})
        print(f"Updated existing governance comment id={cid}")
    else:
        gh_request("POST", base, token, {"body": full_body})
        print("Created new governance comment")


if __name__ == "__main__":
    main()
