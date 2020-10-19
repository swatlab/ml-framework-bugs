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

logger = logging.getLogger()
logger.setLevel(logging.WARNING)

@click.group()
def cli():
    pass

# TODO: Move to class, ex: PyTorchCommitMatcher
def commit_belongs_to_issue(commit_info, issue_number, other_data=None, pr_data=None):
    import git
    if isinstance(commit_info, git.objects.Commit):
        # TODO: Use metadata and other factors to match
        return  f'#{issue_number}' in commit_info.message or f'pull/{issue_number}' in commit_info.message
    else:
        raise NotImplementedError('Need a Python wrapped git object')

def get_commit_for_pr(git_dir, issue_number, other_data=None, pr_data=None):
    import git
    from git import Repo
    import functools

    if isinstance(git_dir, str):
        git_dir = Path(git_dir)

    repo = Repo(git_dir)
    git_cmd = repo.git
    logger.debug('Git version is {}'.format(git_cmd.version()))

    # Optional parameters to git rev-list
    rev_list_kwargs = {}
    fixed_in_release, start_revision = None, None
    if other_data is not None:
        fixed_in_release = other_data.get('release')
    if pr_data is not None:
        start_revision = pr_data['base']['sha']
        try:
            repo.git.rev_parse(start_revision, verify=True)
        except:
            logging.debug('Start revision failed to be verified.')
            start_revision = None

    range_to_search = '{start}..{end}'.format(start=start_revision or '', end=fixed_in_release or '') if start_revision or fixed_in_release else 'origin/master'
    logger.debug('Searching range {}'.format(range_to_search))

    commit_matches = list(filter(functools.partial(commit_belongs_to_issue, issue_number=issue_number, other_data=other_data, pr_data=pr_data),
                    repo.iter_commits(range_to_search, **rev_list_kwargs)))

    logger.info('Search result is {}'.format(commit_matches))
    if len(commit_matches) == 1:
        logger.debug('One commit found that matches our search.')
        return commit_matches[0]
    elif len(commit_matches) == 0:
        logger.info('No commit matched the search result.')
        return None
    elif len(commit_matches) >= 2:
        logger.info('Multiple commit matched:')
        for matched_commit in commit_matches:
            logger.debug('{}: {}'.format(matched_commit.hexsha, matched_commit.summary))
        return None


def task(executable_path, issue_number, env, write_root_path, quiet=True):
    """Execute a search commit script given an issue number and writes script results."""
    with open(Path('{}/{}.txt'.format(write_root_path, issue_number)), 'w') as of:
        cp = subprocess.run([executable_path, '--strict' ,'--no-color', str(issue_number)], env=env, stdout=of, stderr=of)
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
@click.option('--strict', is_flag=True)
def pr_merged_points(framework, git_dir, pull_request_file, strict):
    """Get the before and after commit for pull request issue that was merged."""
    # TODO: Make util
    import pull_request
    git_path = Path(git_dir)
    df = pd.read_csv(pull_request_file)
    logger.debug(df.columns)

    root_path = Path('out').joinpath(framework.lower())
    p_input_dir = root_path / 'pull_requests'
    p_output_dir = root_path / 'processed_v2'
    
    with click.progressbar(df.iterrows(), length=len(df),
                            label="Finding commits for Pull Requests",
                            show_eta=True, show_pos=True,
                            bar_template="%(label)s [%(bar)s] %(info)s") as bar:
        for i, row in bar:
            issue_number = row.issue_number
            logger.debug('Iteration {}'.format(type(i)))
            logger.info('Getting issue for {}'.format(issue_number))
            try:
                pr_data = pull_request.get_local_pr(p_input_dir, issue_number, use_json=True)
            except:
                logger.debug('Failed to get local data for pull request')
                pr_data = None
            try:
                commit_info = get_commit_for_pr(git_path, issue_number, other_data=row, pr_data=pr_data)
            except Exception as err:
                logger.error('Failed to get commit for unhandled exception.')
                commit_info = None

            if strict:
                assert commit_info is not None
            if commit_info is not None:
                logger.info('Commit for PR {} is {}'.format(issue_number, commit_info))
                corrected, buggy = commit_info.hexsha, commit_info.parents[0].hexsha
                df.loc[i, 'buggy_commit'] = buggy
                df.loc[i, 'corrected_commit'] = corrected
                logger.info('Corrected for PR {} is {}'.format(issue_number, corrected))
                logger.info('Buggy for PR {} is {}'.format(issue_number, buggy))

    df.to_csv(p_output_dir / 'concat_v3.csv', index=False)

@cli.command()
@click.option('--framework', type=click.Choice(['PyTorch'], case_sensitive=False), default='PyTorch')
@click.option('--git-dir', '-d', type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.option('--pull-request-file', '-f', type=click.Path(exists=True, dir_okay=False))
@click.option('--bash-script-file', type=click.Path(dir_okay=False, resolve_path=True), default=None)
@click.option('--parallel', is_flag=True)
def locally(framework, git_dir, pull_request_file, bash_script_file, parallel):
    """Extract commit and branching information for Pull Requests in cloned repository.
    
    Reads a local csv (`pull-request-file`) containing all the pull requests and reads
    the `issue_number` value to launch a search script in the `git-dir`.
    """
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
