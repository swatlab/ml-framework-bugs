from repos import FRAMEWORK_MAPPING
from repo_configuration import RepoConfiguration
import argparse

PARSER = argparse.ArgumentParser()

PARSER.add_argument('--repo', choices=FRAMEWORK_MAPPING.keys(), required=True)
PARSER.add_argument('--issue', type=int, required=True)

def extract_commits(repo: RepoConfiguration, issue: int):
    fix_commit, parent_commit = repo.commits_for_issue(issue)
    print('Issue:', issue)
    print('Buggy commit:', parent_commit)
    print('Fix commit:', fix_commit)


if __name__ == "__main__":
    ARGS = PARSER.parse_args()
    extract_commits(repo=FRAMEWORK_MAPPING[ARGS.repo], issue=ARGS.issue)