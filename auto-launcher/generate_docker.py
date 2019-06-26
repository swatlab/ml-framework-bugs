import os
import abc
import shutil
from pathlib import Path
from repos import FRAMEWORK_MAPPING, PyTorchRepo
from repo_configuration import EvaluationType, StrategyType, EVALUATION_TYPES, RepoConfiguration

# TODO: Parametrize Strategy type


def _generate_docker(framework, commit, output_file):
    with open(framework.dockerfile_path, 'rt') as input_file:
        fc = input_file.read()
    content = fc.replace('COMMIT_PLACEHOLDER', commit)
    with open(output_file, 'w') as of:
        of.write(content)


def config_for_issue(framework: RepoConfiguration, issue):
    # TODO: Create 3 Dockerfiles (3 versions: buggy, non-buggy and AutoML on non buggy)
    output_dir = Path('configs/{}/{}'.format(framework.name, issue))
    output_dir.mkdir(parents=True, exist_ok=True)

    for ev_type, ev_name in EVALUATION_TYPES.items():
        new_filename = 'Dockerfile_f{}_i{}_v{}'.format(framework.name, issue, ev_name)
        new_file_path = output_dir / new_filename
        # _generate_docker(framework, version_to_checkout, output_file=new_file_path)
        # content = framework.generate_docker_content(issue=issue, strategy=StrategyType.RELEASE_BETWEEN, eval_type=ev_type)
        content = build_dockerfile_along_strategy(strategy=StrategyType.RELEASE_BETWEEN, repo_instance=framework, issue=issue, eval_type=ev_type)
        with open(new_file_path, 'w') as of:
            of.write(content)


def build_dockerfile_along_strategy(strategy: StrategyType, repo_instance: RepoConfiguration, issue, eval_type: EvaluationType):
    # TODO: Put a map for better dispatch?
    if isinstance(repo_instance, PyTorchRepo):
        content = PyTorchDockerBuilder(repo_instance, strategy).build_dockerfile(issue, eval_type)
    else:
        raise NotImplementedError("Not implemented for {}".format(type(repo_instance)))
    return content


class RepoDockerBuilder(object):
    def __init__(self, repo_instance: RepoConfiguration, generation_strategy: StrategyType):
        self.repo = repo_instance
        self.generation_strategy = generation_strategy

    def build_dockerfile(self, issue, evaluation_type, **kwargs):
        fix_commit, parent_commit = self.repo.commits_for_issue(issue)
        # TODO: Correctly infer CUDA version or CPU only
        CUDA_VERSION = kwargs.get('CUDA_VERSION', 9.0)  # Put None to disable
        if self.generation_strategy == StrategyType.RELEASE_BETWEEN:
            latest_release_tag = self.repo.latest_release_tag_for_commit(fix_commit)
            prior_release_tag = self.repo.tag_prior_to_tag(latest_release_tag)
            tag_to_position = latest_release_tag if evaluation_type == EvaluationType.FIXED else prior_release_tag
            return self.release_between(tag_to_position, CUDA_VERSION)
        elif self.generation_strategy == StrategyType.BUILD_BETWEEN:
            # Only the 'fixed' version needs to be on the commit of the fix
            version_to_checkout = fix_commit if evaluation_type == EvaluationType.FIXED else parent_commit
            return self.build_between(version_to_checkout, CUDA_VERSION)

    @abc.abstractclassmethod
    def build_between(self, version_to_checkout):
        pass

    @abc.abstractclassmethod
    def release_between(self, tag_to_position):
        pass


class PyTorchDockerBuilder(RepoDockerBuilder):
    def build_between(self, version_to_checkout):
        # Only the 'fixed' version needs to be on the commit of the fix
        with open(self.repo.dockerfile_path, 'rt') as input_file:
            fc = input_file.read()
        content = fc.replace('COMMIT_PLACEHOLDER', version_to_checkout)
        return content

    def release_between(self, tag_to_position, cuda_version):
        conda_cuda_version = '{0:0>2d}'.format(int(cuda_version*10))
        repl_dict = {
            # TODO: Smart formatting
            'conda_install_command': 'conda install pytorch={} {} -c pytorch'.format(tag_to_position.lstrip('v'), 'cuda{}'.format(conda_cuda_version)),
            'base_image': 'nvidia/cuda:{}-cudnn7-devel-ubuntu16.04'.format(cuda_version) if cuda_version else 'TODO'
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

if __name__ == "__main__":
    # TODO: Put this as an option
    F = FRAMEWORK_MAPPING['pytorch']
    config_for_issue(F, issue='10066')
