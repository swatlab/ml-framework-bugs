import click
import os
import subprocess
import bug_extraction.data_utils as du
import code_inserter.trace_inserter as trace_inserter
import logging
import pandas as pd
from pathlib import Path
import colorama

logger = logging.getLogger()


@click.group()
def cli():
    pass


def changes_cuda_related(file_changes):
    # TODO Better
    for fn in file_changes:
        p = Path(fn)
        if p.suffix == 'cuh' or p.suffix == 'cu':
            return True
        if 'cuda' in fn or 'cudnn' in fn:
            return True
    return False


def git_cmd(git_dir, cmd, *args, **kwargs):
    assert isinstance(cmd, str)
    if not isinstance(git_dir, Path):
        git_dir = Path(git_dir)
    # logger.info('Dir is {}'.format(git_dir))
    env_copy = os.environ.copy()
    cli_args, cli_options = [], []
    for v in args:
        cli_args.append(v)

    for k,v in kwargs.items():
        if len(k) == 1:
            cli_options.append('-{}'.format(k))
        else:
            _k = k.replace('_', '-')
            cli_options.append('--{}'.format(_k))
        if v is not None:
            cli_options.append(v)
    logger.debug('git {cmd} {options} {args}'.format(cmd=cmd, options=' '.join(cli_options), args=' '.join(cli_args)))
    env_copy['GIT_DIR'] = git_dir
    result_cmd = subprocess.run(['git', cmd, *cli_options ,*cli_args], capture_output=True, env=env_copy, cwd=git_dir.parent)
    logger.debug(result_cmd)
    return result_cmd.returncode, result_cmd.stdout.decode("utf-8")

def long_commit_version(git_dir, sha):
    err, v = git_cmd(git_dir, 'rev-parse', sha, verify=None)
    if err != 0:
        raise Exception('Unable to parse version')
    return v.strip()


# To clear branches locally, you can
# git branch -l 'study*'|xargs git branch -D

def ensure_path(p):
    if not isinstance(p, Path):
        return Path(p)

def file_was_deleted(git_dir, path, pre, post):
    err, name_statuses = git_cmd(git_dir, 'diff', pre, post, name_status=None)
    # TODO: Better
    p = ensure_path(git_dir).parent
    f = str(path.relative_to(p))
    for ns in name_statuses.splitlines():
        if f in ns:
            # First char is status
            if ns[0] in {'D','A'}:
                return True
    return False


@cli.command()
@click.argument('csv_file', type=click.Path(dir_okay=False, exists=True))
@click.option('--git-dir', '-d', type=click.Path(exists=True, file_okay=False, resolve_path=True), required=True)
@click.option('--all', '-a', 'use_all', is_flag=True, help='Look through every row even those who do not qualif for study')
@click.option('--insert-trace/--no-insert-trace', default=True)
@click.option('--setup-branch/--no-setup-branch', default=True)
@click.pass_context
def setup_study(ctx, csv_file, git_dir, use_all, insert_trace, setup_branch):
    """ Reads from CSV file and creates appropriate branching structure
    
    Inserts trace optionnaly.
    """
    # TODO: Get CSV from data_utils
    df = du.get_csv(csv_file)
    logger.debug(df.shape)
    logger.debug(df.columns)
    logger.debug(df.dtypes)
    treatable_c, cuda_related_c = 0, 0
    
    original_shape = df.shape

    rdf = df[(df.use_for_study != 'no') & (df.use_for_study != '') & (~pd.isna(df.use_for_study))]
    if use_all:
        logger.info('Using entire dataframe')
        rdf = df

    c_trace_header = """#include <lttng/tracef.h>"""
    # Check if we should customize per study
    c_trace_content= """tracef("TracePoint: Bug Triggered");"""
    py_trace_header = ""
    # Check if we should customize per study
    py_trace_content = """print("Tracepoint Bug Triggered")"""
    
    logger.info('{} rows used as starting point'.format(rdf.shape[0]))
    for i, (loc, row) in enumerate(rdf.iterrows()):
        bid = row['pr_number']  # Bug identifier
        xp_n = 'study-pr{}'.format(bid)
        logger.info('[{}/{}] Bug/Experiment name {}'.format(i, len(rdf), xp_n))
        bg_cm, cor_cm = row['buggy_commit'], row['corrected_commit']
        if pd.isna(bg_cm) or pd.isna(cor_cm):
            logger.info('No buggy or corrected commit found for row {}'.format(xp_n))
            continue
        treatable_c += 1

        logger.info('Buggy commit: {}'.format(bg_cm))
        logger.info('Corrected commit: {}'.format(cor_cm))

        # Get files that changed between both commits
        file_changes = trace_inserter.diff_file_paths(git_dir, bg_cm, cor_cm)
        logger.info(file_changes)
        has_cuda = changes_cuda_related(file_changes)
        if has_cuda:
            cuda_related_c += 1
            logger.info('Experience {} is CUDA related'.format(xp_n))

        study_branch, study_branch_buggy, study_branch_corrected  = xp_n, f'{xp_n}-buggy', f'{xp_n}-corrected'
        long_bug = long_commit_version(git_dir, bg_cm)
        long_cor = long_commit_version(git_dir, cor_cm)
        assert long_bug != '' and long_cor != ''

        do_commit = True
        full_auto_trace = True

        if setup_branch:
            # 1 Check if branch exists
            # 2 create branch `xp_n` at corrected
            # 3 checkout branch at `xp_n`
            # 4 revert corrected
            # 5 create branch `xp_n`-corrected from revert
            # 6 revert revert
            # 7 create branch `xp_n`-buggy

            ret, out = git_cmd(git_dir, 'rev-parse', study_branch, quiet=None, verify=None)
            logger.debug('Got return code {}'.format(ret))
            logger.debug('Got output {}'.format(out))
            if ret == 0:
                # Branch exists, just checkout
                git_cmd(git_dir, 'checkout', study_branch)
            else:
                # Ok to create branch name `study_branch` (study branch) starting at `cor_cm` (corrected commit)
                git_cmd(git_dir, 'checkout', cor_cm , B=study_branch)

            # Now at study branch, ex `study-prXXXX`
            pointing = long_commit_version(git_dir, 'HEAD')
            parent = long_commit_version(git_dir, 'HEAD^')
            if pointing == long_cor:
                # study branch still points at corrected version, we revert it
                # assert long_commit_version(git_dir, 'HEAD')[1] == long_cor
                # Revert long_cor which should be HEAD
                err, out = git_cmd(git_dir, 'revert', long_cor, no_edit=None)
                assert err == 0
            else:
                logger.debug('Pointing commit is {}'.format(pointing))
                logger.debug('Parent commit is {}'.format(parent))
                # Study branch pointing at another commit.
                # Check if parent is corrected commit
                assert parent == long_cor
                # Past this point, the commit should be a revert,
                logger.warning('No revert done because commit {} exists at branch {}'.format(pointing, study_branch))

            # 5 create new branch from `study_branch` and checkout `study_branch_corrected`
            git_cmd(git_dir, 'checkout', study_branch , B=study_branch_corrected)
            # Make sure commit pointed by our corrected study branch is the same as the first revert
            assert long_commit_version(git_dir, study_branch_corrected)[1] == long_commit_version(git_dir, study_branch)[1]
            # Revert `study_branch`, which points at the revert
            git_cmd(git_dir, 'revert', study_branch, no_edit=None)

            # Branch from initial revert to new branch `bt_buggy`
            git_cmd(git_dir, 'checkout', study_branch, B=study_branch_buggy)

            # We should now have 3 branches for the one study, all starting from corrected commit
        top_level = git_cmd(git_dir, 'rev-parse', show_toplevel=None)[1].strip()
        if insert_trace:
            trace_output_p = Path('out/trace_insertions/{}'.format(xp_n))
            trace_output_p.mkdir(exist_ok=True,parents=True)

            for t in {'buggy', 'corrected'}:
                logger.info('Trace inserting for type {}'.format(t))
                if t == 'buggy':
                    # Checkout buggy branch
                    err, _ = git_cmd(git_dir, 'checkout', study_branch_buggy)
                else:
                    err, _ = git_cmd(git_dir, 'checkout', study_branch_corrected)
                assert err == 0
                # TODO: Decide if commit in between
                for f_ix, file_c in enumerate(file_changes):
                    logging.debug('Treating {}'.format(file_c))
                    _f = Path(file_c)
                    repo_file_path = Path(top_level).joinpath(_f)
                    # File deletion does not wrk in this case
                    # if t == 'buggy':
                    #     pre = 
                    if file_was_deleted(git_dir, repo_file_path, bg_cm, cor_cm):
                        logging.info('File {} was deleted in post. Skipping...'.format(repo_file_path))
                        continue
                    assert repo_file_path.exists()

                    prompt_ctx = colorama.Fore.BLUE + "{}[{}/{}] File {}".format(t, f_ix, len(file_changes), repo_file_path) + colorama.Fore.RESET
                    # For buggy version, use insert_pre=True
                    if t == 'buggy':
                        # For buggy version, use insert_pre=True
                        fc, lines_changed = trace_inserter.get_content_and_changed_lines(git_dir, file=file_c, pre=bg_cm, post=cor_cm, insert_pre=True)
                    else:
                        # For corrected version, use inser_post=True
                        fc, lines_changed = trace_inserter.get_content_and_changed_lines(git_dir, file=file_c, pre=bg_cm, post=cor_cm, insert_post=True)

                    if _f.suffix in {'.cpp', '.h'}:
                        trace_content, trace_header = c_trace_content, c_trace_header
                    elif _f.suffix in {'.cu', '.cuh'}:
                        logger.warning('Cannot insert traces in CUDA file at the moment. Skipping file...')
                        continue
                    elif _f.suffix in {'.py'}:
                        trace_content, trace_header = py_trace_content, py_trace_header
                    else:
                        logger.warning("File not supported for trace insertion: {}".format(file_c))

                    # See `trace_inserter.insert_trace` for full signature
                    new_file_content = trace_inserter.insert_trace(fc, lines_changed,
                        what=trace_content, header=trace_header,
                        do_prompt=not full_auto_trace,
                        filename=file_c,
                        prompt_ctx=prompt_ctx)

                    if do_commit:
                        with open(repo_file_path, 'w') as f:
                            f.write(new_file_content)
                if do_commit:
                    commit_message = """ "Study: Add traced content" """
                    # TODO: Treat file individually
                    # err, mes = git_cmd(git_dir, 'add', *file_changes)
                    err, mes = git_cmd(git_dir, 'commit', '-am', commit_message)
                    assert err == 0

    logger.info('CUDA related commit: {}'.format(cuda_related_c))
    logger.info('Treatable commit: {}'.format(treatable_c))


if __name__ == "__main__":
    logging.root.setLevel(logging.NOTSET)
    console_h = logging.StreamHandler()
    console_h.setLevel(logging.INFO)
    debug_fh = logging.FileHandler('debug.log', mode='w')
    debug_fh.setLevel(logging.DEBUG)
    logger.addHandler(debug_fh)
    logger.addHandler(console_h)
    cli()

