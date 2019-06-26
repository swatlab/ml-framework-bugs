import abc
import subprocess
from pathlib import Path
from enum import Enum, unique

@unique
class EvaluationType(Enum):
    BUGGY = 1
    FIXED = 2
    AUTOML = 3

@unique
class StrategyType(Enum):
    RELEASE_BETWEEN = 1
    BUILD_BETWEEN = 2

EVALUATION_TYPES = {
    EvaluationType.BUGGY: 'buggy',
    EvaluationType.FIXED: 'fixed',
    EvaluationType.AUTOML: 'automl'
}

class RepoConfiguration(abc.ABC):
    def __init__(self, name, dockerfile_path, local_repo_path=None):
        self.dockerfile_path = Path(dockerfile_path)
        self.name = name
        assert self.dockerfile_path.exists()
        if local_repo_path:
            p = Path(local_repo_path)
            assert p.exists()
            self._local_repo_path = p

    def parent_commit(self, commit_sha, check_sha=False):
        if check_sha:
            # TODO: Verification that commit_sha exists
            pass
        log_proc = subprocess.run('git rev-parse {}^ --format="%h"'.format(commit_sha), cwd=self.local_path, stdout=subprocess.PIPE, shell=True, stderr=None, check=check_sha)
        parent_split = log_proc.stdout.decode('utf8').split('\n')
        return parent_split[0]

    @abc.abstractmethod
    def commits_for_issue(self, issue):
        pass

    @abc.abstractmethod
    def latest_release_tag_for_commit(self, issue):
        pass

    @property
    def local_path(self):
        return self._local_repo_path