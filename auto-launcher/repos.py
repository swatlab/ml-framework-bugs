import abc
import subprocess
from typing import Dict
from repo_configuration import RepoConfiguration, EvaluationType, StrategyType, EVALUATION_TYPES

RepoMapping = Dict[str, RepoConfiguration]

class PyTorchRepo(RepoConfiguration):
    def _commit_fixing_issue(self, issue):
        cmd_to_run = 'git log -i --grep="(#{})" --format="%h"'.format(issue)
        log_proc = subprocess.run(cmd_to_run, cwd=self.local_path, stdout=subprocess.PIPE, shell=True, stderr=None, check=True)
        commits = log_proc.stdout.decode('utf8')
        split = commits.split('\n')
        if len(split) > 2:
            raise Exception('More than two commits detected', cmd_to_run, split)
        else:
            fix_commit = split[0]
        return fix_commit

    def commits_for_issue(self, issue):
        fix_commit = self._commit_fixing_issue(issue)
        return fix_commit, self.parent_commit(fix_commit)
    
    def latest_release_tag_for_commit(self, commit):
        log_proc = subprocess.run('git tag --contains {}'.format(commit), cwd=self.local_path, stdout=subprocess.PIPE, shell=True, stderr=None, check=False)
        latest_tag_decoded = log_proc.stdout.decode('utf8')
        lateest_tag = latest_tag_decoded.split('\n')
        return lateest_tag[0]

    def tag_prior_to_tag(self, tag):
        if not hasattr(self, '_tag_cache'):
            tags_output = subprocess.run("git for-each-ref --sort=taggerdate --format='%(refname:short)' refs/tags", cwd=self.local_path, stdout=subprocess.PIPE, shell=True, stderr=None, check=False)
            tags_decoded = tags_output.stdout.decode('utf8')
            self._tag_cache = tags_decoded.split('\n')
        tag_index = self._tag_cache.index(tag)
        if tag_index == 0:
            raise Exception('There is no tag prior to the first tag ({})'.format(tag))
        prior_tag = self._tag_cache[tag_index - 1]
        return prior_tag


# TODO: Make config file available to read these values
PyTorchRepo_instance = PyTorchRepo(name='PyTorch',
                                    dockerfile_path='configs/PyTorch/Dockerfile_PyTorch',
                                    local_repo_path='/home/emilio/Repos/frameworks/pytorch/')

FRAMEWORK_MAPPING: RepoMapping = {
    'pytorch': PyTorchRepo_instance
}
