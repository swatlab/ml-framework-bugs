import abc
import subprocess
from typing import Dict
from repo_configuration import RepoConfiguration, EvaluationType, StrategyType, EVALUATION_TYPES

RepoMapping = Dict[str, RepoConfiguration]

class PyTorchRepo(RepoConfiguration):
    def _commit_fixing_issue(self, issue):
        log_proc = subprocess.run('git log -i --grep="(#{})" --format="%h"'.format(issue), cwd=self.local_path, stdout=subprocess.PIPE, shell=True, stderr=None, check=False)
        commits = log_proc.stdout.decode('utf8')
        split = commits.split('\n')
        if len(split) > 2:
            raise Exception('More than two commits detected')
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
            print(tags_decoded)
        tag_index = self._tag_cache.index(tag)
        if tag_index == 0:
            raise Exception('There is no tag prior to the first tag ({})'.format(tag))
        prior_tag = self._tag_cache[tag_index - 1]
        return prior_tag

    def generate_docker_content(self, issue, strategy, eval_type):
        # TODO: Correctly use AutoML type
        fix_commit, parent_commit = self.commits_for_issue(issue)
        # TODO: Correctly infer CUDA version or CPU only
        CUDA_VERSION = 9.0 # Put None to disable
        if strategy == StrategyType.BUILD_BETWEEN:
            # Only the 'fixed' version needs to be on the commit of the fix
            version_to_checkout = fix_commit if eval_type == EvaluationType.FIXED else parent_commit
            with open(self.dockerfile_path, 'rt') as input_file:
                fc = input_file.read()
            content = fc.replace('COMMIT_PLACEHOLDER', commit)
            return content
        elif strategy == StrategyType.RELEASE_BETWEEN:
            latest_release_tag = self.latest_release_tag_for_commit(fix_commit)
            prior_release_tag = self.tag_prior_to_tag(latest_release_tag)
            tag_to_position = latest_release_tag if eval_type == EvaluationType.FIXED else prior_release_tag
            conda_cuda_version = '{0:0>2d}'.format(int(CUDA_VERSION*10))
            repl_dict = {
                # TODO: Smart formatting
                'conda_install_command': 'conda install pytorch={} {} -c pytorch'.format(tag_to_position.lstrip('v'), ''),
                'base_image': 'nvidia/cuda:{}-cudnn7-devel-ubuntu16.04'.format(CUDA_VERSION) if CUDA_VERSION else 'TODO'
            }
            content = """\
FROM {base_image}
ARG PYTHON_VERSION=3.6
RUN apt-get update && apt-get install -y --no-install-recommends \\
         build-essential \\
         cmake \\
         git \\
         curl \\
         ca-certificates \\
         libjpeg-dev \\
         libpng-dev
RUN curl -o ~/miniconda.sh -O  https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh  && \\
     chmod +x ~/miniconda.sh && \\
     ~/miniconda.sh -b -p /opt/conda && \\
     rm ~/miniconda.sh && \\
     /opt/conda/bin/conda install -y python=$PYTHON_VERSION numpy pyyaml scipy ipython mkl mkl-include ninja cython typing && \\
     /opt/conda/bin/conda clean -ya
ENV PATH /opt/conda/bin:$PATH

RUN {conda_install_command}
""".format_map(repl_dict)
            return content
            # TODO: Correctly put information in Dockerfile

# TODO: Make config file available to read these values
PyTorchRepo_instance = PyTorchRepo(name='PyTorch',
                                    dockerfile_path='configs/PyTorch/Dockerfile_PyTorch',
                                    local_repo_path='/home/emilio/Repos/frameworks/pytorch/')

FRAMEWORK_MAPPING: RepoMapping = {
    'pytorch': PyTorchRepo_instance
}
