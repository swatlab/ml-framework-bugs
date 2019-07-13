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

    def parent_commit(self, commit_sha, check_sha=True):
        if check_sha:
            if commit_sha == '':
                raise ValueError('commit_sha is empty   ')
            exist_proc = subprocess.run('git branch --contains "{}" '.format(commit_sha), cwd=self.local_path, stdout=subprocess.PIPE, shell=True, stderr=None, check=True)
        try:
            log_proc = subprocess.run('git rev-parse --verify  {}^'.format(commit_sha), cwd=self.local_path, stdout=subprocess.PIPE, shell=True, stderr=None, check=True)
            parent_split = log_proc.stdout.decode('utf8').split('\n')
        except subprocess.CalledProcessError as e:
            print('Error with calling parent_commit with input: BEGIN OF INPUT--', commit_sha, '-- END OF INPUT')
            print(e)
            raise
        else:
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