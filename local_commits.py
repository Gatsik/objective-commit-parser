import csv
import json  # not used, but adds COCOCO
import logging
import os
from collections import Counter

import _csv
import coloredlogs
import git
import whatthepatch
from git.objects.commit import Commit
from tqdm import tqdm

from parse_commits import code_quantity, commit_quality

MAXIMUM_COMMIT_LIMIT_PER_REPOSITORY = 10_000


def parse_commit(commit: Commit) -> dict[str, int]:
    quantity: dict[str, int] = Counter()
    raw_patch = commit.repo.git.show(commit)
    patches = list(whatthepatch.parse_patch(raw_patch))
    for patch in patches:
        if patch.changes is None:
            continue
        for change in patch.changes:
            if change.new is None:
                continue
            stats = code_quantity(change.line)
            quantity.update(stats)
    quality = commit_quality(commit.message)

    return {
        "quantity": quantity["cococo"],
        "quality": quality,
    }


def parse_repo_commits(repo_path: str, results_writer: "_csv._writer") -> None:
    repo = git.Repo(repo_path)
    iterator = repo.iter_commits(max_count=MAXIMUM_COMMIT_LIMIT_PER_REPOSITORY)
    for commit in tqdm(list(iterator)):
        commit_results = parse_commit(commit)
        results_writer.writerow([
            commit_results["quantity"],
            commit_results["quality"],
            commit.message,
            commit.author.name if commit.author else '',
            os.path.basename(os.path.dirname(repo.common_dir)),
        ])


def main() -> None:
    coloredlogs.install(level=logging.INFO)

    with open("python_repositories.txt") as fd:
        repo_paths = fd.readlines()

    os.makedirs("results", exist_ok=True)

    with open("results/data.csv", "w") as rfile:
        writer = csv.writer(rfile, quoting=csv.QUOTE_ALL)
        writer.writerow([
            "code_quantity",
            "commit_quality",
            "message",
            "author",
            "repo",
        ])
        for path in repo_paths:
            logging.info(f"Processing repo {path}")
            parse_repo_commits(path.strip(), writer)


if __name__ == "__main__":
    raise SystemExit(main())
