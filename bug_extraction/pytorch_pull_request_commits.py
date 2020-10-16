"""
Goal: Extract information about commits from a Pull Request number,
      assuming we have a LOCAL repository clone.
"""
import os
import glob
import logging
import pandas as pd
import click
from pathlib import Path, PurePath
import subprocess

logging.basicConfig(level=logging.INFO)

@click.group()
def cli():
    pass

def task(executable_path, issue_number, env, write_root_path, quiet=True):
    with open(Path('{}/{}.txt'.format(write_root_path, issue_number)), 'w') as of:
        cp = subprocess.run([executable_path, '--strict', '--silent' ,'--no-color', str(issue_number)], env=env, stdout=of, stderr=of)
        if cp.returncode != 0 and not quiet:
            logging.error('Task {} exited with an error'.format(issue_number))
    return cp.returncode

import enum
class GitResultStatusCode(enum.IntEnum):
    FAILED_ON_PYTHON = 4

@cli.command()
@click.option('--framework', type=click.Choice(['PyTorch'], case_sensitive=False), default='PyTorch')
@click.option('--git-dir', '-d', type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.option('--pull-request-file', '-f', type=click.Path(exists=True, dir_okay=False))
@click.option('--bash-script-file', type=click.Path(dir_okay=False, resolve_path=True), default=None)
@click.option('--parallel', is_flag=True)
def locally(framework, git_dir, pull_request_file, bash_script_file, parallel):
    import time
    df = pd.read_csv(pull_request_file)
    n = len(df.issue_number)
    def show_prog_item(item):
        return f"Pull Request #{item}"

    git_path = Path(git_dir)
    if git_path.name != '.git':
        logging.warning('Passed argument "{}" for git directory should point to a .git/ folder'.format(git_path))
        # TODO: Check if still want
        logging.warning('Adding .git/ to path')
        git_path = git_path.joinpath('.git/')

    sp_env_vars = os.environ.copy()
    if bash_script_file:
        sp_env_vars.update({'GIT_DIR': git_path})
        logging.info('Will call bash script file {}'.format(bash_script_file))

    output_root_path = Path('out/{}/diffs'.format(framework.lower()))

    with click.progressbar(df.issue_number.values, length=n,
                            item_show_func=show_prog_item,
                            label="Finding commits for Pull Requests",
                            show_eta=True, show_pos=True,
                            bar_template="%(label)s [%(bar)s] %(info)s") as bar:
        import functools, itertools
        if parallel:
            import multiprocessing
            return_codes, tasks = [], []

            def err_handler(*args, **kwargs):
                logging.error('Got error!')
                logging.debug('Error handler {}'.format(args))
                return_codes.append(GitResultStatusCode.FAILED_ON_PYTHON)
            def done_handler(ret_code, *args):
                logging.debug('Done handler got statuscode {}'.format(ret_code))
                return_codes.append(ret_code)

            with multiprocessing.Pool(8) as p:
                for i in range(n):
                    r = p.apply_async(task, (bash_script_file, df.issue_number.iloc[i], sp_env_vars, output_root_path), callback=done_handler, error_callback=err_handler)
                    tasks.append(r)
                for t, _ in zip(tasks, bar):
                    # Append result from task which is status code or None if failed somwhere in between (in Python)
                    # in that case, return own enum value
                    res = t.wait()
                    logging.debug('In zip with wait val {}'.format(res))

            assert len(return_codes) == n == len(tasks)
            logging.debug(return_codes)
            logging.debug(tasks)

            if sum(return_codes) == 0:
                logging.info('All tasks return code 0. Completed {} out of {} tasks!'.format(len(return_codes), n))
            else:
                n_failed = sum(1 for ret in return_codes if ret != 0)
                n_success = len(return_codes) - n_failed
                logging.warning('There are {} failed tasks (return code not 0). Check output'.format(n_failed))
                logging.info('Completed {} out of {} tasks.'.format(n_success, n))
        else:
            for issue_number in bar:
                if bash_script_file:
                    task(bash_script_file, str(issue_number), sp_env_vars, output_root_path)
                else:
                    raise NotImplementedError()


if __name__ == "__main__":
    cli()
