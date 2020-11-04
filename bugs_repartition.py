import click
import os
import subprocess
import bug_extraction.data_utils as du
import code_inserter.trace_inserter as trace_inserter
import logging
import pandas as pd
from pathlib import Path

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
    return git_cmd(git_dir, 'rev-parse', sha, verify=None)


# To clear branches locally, you can
# git branch -l 'study*'|xargs git branch -D


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
    c_trace_content= """tracef("TracePoint: BugTriggered");"""
    py_trace_header = ""
    py_trace_content = """print("Tracepoint BugTriggered")"""
    

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

        file_changes = trace_inserter.diff_file_paths(git_dir, bg_cm, cor_cm)
        logger.info(file_changes)
        has_cuda = changes_cuda_related(file_changes)
        if has_cuda:
            cuda_related_c += 1
            logger.info('Experience {} is CUDA related'.format(xp_n))

        study_branch, study_branch_buggy, study_branch_corrected  = xp_n, f'{xp_n}-buggy', f'{xp_n}-corrected'
        _, long_bug = long_commit_version(git_dir, bg_cm)
        _, long_cor = long_commit_version(git_dir, cor_cm)
        assert long_bug != '' and long_cor != ''

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
            _, pointing = long_commit_version(git_dir, 'HEAD')
            _, parent = long_commit_version(git_dir, 'HEAD^')
            if pointing == long_cor:
                # study branch still points at corrected version, we revert it
                # assert long_commit_version(git_dir, 'HEAD')[1] == long_cor
                # Revert long_cor which should be HEAD
                git_cmd(git_dir, 'revert', long_cor, no_edit=None)
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

        if insert_trace:
            trace_output_p = Path('out/trace_insertions/{}'.format(xp_n))
            trace_output_p.mkdir(exist_ok=True,parents=True)

            # Buggy commit trace insertion
            # Trace insert considers the post version to put the traces
            # so...
            logger.info('Trace inserting for type buggy')
            ctx.invoke(trace_inserter.diff, pre=bg_cm, post=cor_cm, git_dir=git_dir,
                output_dir=trace_output_p / 'buggy',
                write=True, prompt=True, insert_pre=True,
                c_trace_header=c_trace_header,
                c_trace_content=c_trace_content,
                py_trace_header=py_trace_header,
                py_trace_content=py_trace_content,
                yes=True)
            
            # Corrected commit trace insertion
            logger.info('Trace inserting for type corrected')
            ctx.invoke(trace_inserter.diff, pre=bg_cm, post=cor_cm, git_dir=git_dir,
                output_dir=trace_output_p / 'corrected',
                write=True, prompt=True, insert_pre=True,
                c_trace_header=c_trace_header,
                c_trace_content=c_trace_content,
                py_trace_header=py_trace_header,
                py_trace_content=py_trace_content,
                yes=True)
            # ctx.invoke(trace_inserter.diff, pre=bg_cm, post=cor_cm, git_dir=git_dir, output_dir=trace_output_p / 'corrected' , write=True, prompt=True, insert_pre=False, yes=True)

            logging.info('Saving traces to {}'.format(trace_output_p))

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

