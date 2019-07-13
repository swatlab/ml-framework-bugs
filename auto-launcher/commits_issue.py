from pathlib import Path
from repos import FRAMEWORK_MAPPING
from repo_configuration import RepoConfiguration
import argparse

PARSER = argparse.ArgumentParser()

PARSER.add_argument('--repo', choices=FRAMEWORK_MAPPING.keys(), required=True)
g = PARSER.add_mutually_exclusive_group(required=True)
g.add_argument('--issue', type=int)
g.add_argument('--issue-file', type=str)


def extract_commits(repo: RepoConfiguration, issue: int):
    fix_commit, parent_commit = repo.commits_for_issue(issue)
    print('Issue:', issue)
    print('Buggy commit:', parent_commit)
    print('Fix commit:', fix_commit)


def read_issue_file(repo: RepoConfiguration, file_name, save_valid_commits=False, overwrite=True):
    with open(file_name, 'r') as inp_file:
        issues = inp_file.read()
    valid_commits = []
    for issue in issues.splitlines():
        try:
            fix_commit, parent_commit = repo.commits_for_issue(issue)
            print(fix_commit, parent_commit)
            if save_valid_commits:
                valid_commits.extend([fix_commit, parent_commit])
        except Exception as e:
            print('Error at issue', issue)
            print(e)
            continue
    if save_valid_commits:
        f = Path('output_commits.txt')
        if f.exists() and not overwrite:
            raise ValueError('File {} already exists and overwrite is False'.format(f))
        with open('output_commits.txt', 'w') as of:
            of.write('\n'.join(valid_commits))
            print('Wrote to {}'.format(f))


if __name__ == "__main__":
    ARGS = PARSER.parse_args()
    if ARGS.issue_file is not None:
        read_issue_file(repo=FRAMEWORK_MAPPING[ARGS.repo], file_name=ARGS.issue_file, save_valid_commits=True, overwrite=True)
    else:
        extract_commits(repo=FRAMEWORK_MAPPING[ARGS.repo], issue=ARGS.issue)
