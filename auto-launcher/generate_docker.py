import os
import shutil
from pathlib import Path
from repos import FRAMEWORK_MAPPING
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
        content = framework.generate_docker_content(issue=issue, strategy=StrategyType.RELEASE_BETWEEN, eval_type=ev_type)
        with open(new_file_path, 'w') as of:
            of.write(content)


if __name__ == "__main__":
    # TODO: Put this as an option
    F = FRAMEWORK_MAPPING['pytorch']
    config_for_issue(F, issue='10066')
