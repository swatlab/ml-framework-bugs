import glob
import logging
import pandas as pd
import click
from pathlib import Path, PurePath
import dataclasses
logging.basicConfig(level=logging.INFO)

from study_enums import StudyPhase1Field, StudyPhase2Field

@click.group()
def cli():
    pass

# TODO: Add option to output only changes
@cli.command()
@click.option('--framework', type=click.Choice(['PyTorch'], case_sensitive=False), default='PyTorch')
@click.option('--write/--no-write', default=True)
@click.option('--keep-empty', is_flag=True, help='Keep rows that have no issue number in final dataframe(s)')
@click.option('--concatenate', is_flag=True, help='Create a single dataframe containing all information')
def format_extracted_bugs(framework: str, write: bool, keep_empty: bool, concatenate: bool):
    """Formats per-release CSV files to have consistent CSV files column ordering and complete the first research step.

    Looks in the folder `processed` inside framework's root folder for per-release CSV files.
    Writes into a sibling folder `processed_v2`, optionally in a single file.
    """
    root_path = Path('out').joinpath(framework.lower())
    logging.debug(f'Scanning folder {root_path}')

    p_input_dir, p_output_dir = root_path / 'processed', root_path / 'processed_v2'
    p_output_dir.mkdir(exist_ok=True)

    concat_df = []

    phase_1_columns = [f.name for f in dataclasses.fields(StudyPhase1Field)]
    phase_2_columns = [f.name for f in dataclasses.fields(StudyPhase2Field)]

    for f in p_input_dir.glob('*.csv'):
        logging.info(f)
        release_tag = f.stem.lstrip('{}_'.format(framework.lower()))
        df = pd.read_csv(f, dtype={'issue_number':pd.Int32Dtype()})
        df['framework'] = framework
        df['release']  = release_tag
        df = df.reindex(columns=phase_1_columns+phase_2_columns)

        empty_issue_ix = df.issue_number.isna()
        if keep_empty:
            logging.info('Keeping empty issue rows ({})'.format(sum(empty_issue_ix)))
        else:
            logging.info('Dropping empty issue rows ({})'.format(sum(empty_issue_ix)))
            df = df[~empty_issue_ix]

        logging.debug('Columns are now')
        logging.debug(df.columns)
        logging.debug(df.head(2))
        if concatenate:
            logging.debug('Appending dataframe')
            concat_df.append(df)
        elif write:
            nn = p_output_dir / f.name
            logging.info('Writing single dataframe to file {}'.format(nn))
            df.to_csv(nn, index=False)
    else:
        if concatenate:
            logging.debug('Creating the concatanated dataframe')
            logging.info('New dataframe show have length {}'.format(sum([len(d) for d in concat_df])))
            concat_df = pd.concat(concat_df,ignore_index=True)
            concatenated_df_path = p_output_dir / 'concat.csv'
            if write:
                logging.info('Writing concatenated dataframe to file {}'.format(concatenated_df_path))
                concat_df.to_csv(concatenated_df_path, index=False)

if __name__ == "__main__":
    cli()
