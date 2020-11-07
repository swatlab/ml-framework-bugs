import click
import os
import subprocess
import bug_extraction.data_utils as du
import logging
import pandas as pd
from pathlib import Path

logger = logging.getLogger()


@click.group()
def cli():
    pass


@cli.command()
@click.argument('csv_file', type=click.Path(dir_okay=False, exists=True))
@click.option('--output-dir', type=str, default='out/configs')
@click.pass_context
def create_experiments(ctx, csv_file, output_dir):
    """ Reads from CSV file and creates appropriate environment files and commands to run.
    """
    # TODO: Get CSV from data_utils
    df = du.get_csv(csv_file)
    logger.debug(df.shape)
    logger.debug(df.columns)
    logger.debug(df.dtypes)
    
    output_dir = Path(output_dir)
    original_shape = df.shape
    # TODO: Add option to treat all of them
    # For now, we only output the experiments that are `use_for_study` != 'no' and not empty
    df = df[(df.use_for_study != 'no') & (df.use_for_study != '') & (~pd.isna(df.use_for_study))]
    # ... And those who have both artifacts
    df = df[(~pd.isna(df.build_buggy)) & (~pd.isna(df.build_corrected))]
    logger.info('Should treat {} experiments/rows'.format(len(df)))

    logger.info('{} rows used as starting point'.format(df.shape[0]))
    for i, (loc, row) in enumerate(df.iterrows()):
        bid = row['pr_number']  # Bug identifier
        xp_n = row['bug_name']
        logger.info('[{}/{}] Bug/Experiment name {}'.format(i, len(df), xp_n))
        bg_cm, cor_cm = row['buggy_commit'], row['corrected_commit']
        if pd.isna(bg_cm) or pd.isna(cor_cm):
            logger.info('No buggy or corrected commit found for row {}'.format(xp_n))
            continue

        # TODO: Set this variable according to a column
        bug_cuda_enabled = True

        logger.info('Buggy commit: {}'.format(bg_cm))
        logger.info('Corrected commit: {}'.format(cor_cm))
        xp_path = output_dir / xp_n
        xp_path.mkdir(exist_ok=True, parents=True)

        # We have to create three files and an additional optional:
        # 1. buggy.env
        # 2. corrected.env
        # 3. tag

        env_file_template="""
BUG_NAME={experience_name}
CLIENT_MANUAL_DEPENDENCY={git_revision}
EVALUATION_TYPE={evaluation_type}
CLIENT_PY_VERSION=""
MODEL_LIBRARY=pytorch
PY_CACHE_DIR=
USE_BUILD_MKL=0
USE_CUDA={use_cuda}
        """

        buggy_replacements = {'experience_name': xp_n, 'git_revision': bg_cm[:7], 'evaluation_type': 'buggy', 'use_cuda': bug_cuda_enabled}
        corrected_replacements = {'experience_name': xp_n, 'git_revision': cor_cm[:7], 'evaluation_type': 'corrected', 'use_cuda': bug_cuda_enabled}
        # TODO: Replace with python version and let another process deal with this
        release = row['release']
        if release == 'v1.6.0':
            tag = 'py379-cu101'
        elif release in {'v1.5.1', 'v1.5.0', 'v1.4.1', 'v1.4.0', 'v.1.3.1', 'v1.2.0', 'v1.1.0'}:
            tag = 'py367-cu101'
        else:
            logger.warning("Experiment {} has a release that is not supported ({})".format(xp_n, release))
            logger.warning('Skipping...')
            continue

        # First let's do the buggy
        for ev_type in {'buggy', 'corrected'}:
            out_env = xp_path / '{}.env'.format(ev_type)
            replacement = buggy_replacements if ev_type == 'buggy' else corrected_replacements
            with open(out_env, 'w') as of:
                of.write(env_file_template.format(**replacement))
                logger.debug('Wrote to {}'.format(out_env))

        out_tag = xp_path / 'tag'
        with open(out_tag, 'w') as of:
            of.write(tag)

        logger.info('Wrote {} information to {}'.format(xp_n, xp_path))


if __name__ == "__main__":
    logging.root.setLevel(logging.NOTSET)
    console_h = logging.StreamHandler()
    console_h.setLevel(logging.INFO)
    debug_fh = logging.FileHandler('debug.log', mode='w')
    debug_fh.setLevel(logging.DEBUG)
    logger.addHandler(debug_fh)
    logger.addHandler(console_h)
    cli()

