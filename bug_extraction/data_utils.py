import pandas as pd
from pathlib import Path
import dataclasses
import study_enums
from collections import ChainMap
import logging
import click


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def get_csv(path, nullable=True, strict=True):
    if isinstance(path, str):
        path = Path(path)
    sf_1 = dataclasses.fields(study_enums.StudyPhase1Field)
    sf_2 = dataclasses.fields(study_enums.StudyPhase2Field)
    s1 = { f.name: f.type for f in sf_1 }
    s2 = { f.name: f.type for f in sf_2 }

    def col_mapper(_type):
        if _type == int:
            return pd.Int32Dtype()
        else:
            return _type

    all_cols = ChainMap(s1, s2)

    df = pd.read_csv(path, dtype={ k: col_mapper(t) for k, t in all_cols.items() })
    if strict:
        assert set(df.columns).issubset(set(df.columns))
    return df

@click.group()
def cli():
    pass


def merge_to_mother_dataframe(new_df, mother_df, columns, overwrite_columns=True, can_have_new_columns=False, drop_duplicates=True):
    """Update the mother dataframe with the new information is new_df.

    Output has same order as mother_df.
    Keeps the existing values.
    Columns are the values to update.
    Warning: does not support missing indices.
    """
    if isinstance(new_df, (str, Path)):
        read_df_path = Path(new_df)
        logger.info('Received string as mother_df, will read file at {}'.format(read_df_path))
        new_df = get_csv(read_df_path)
        del read_df_path

    if isinstance(mother_df, (str, Path)):
        read_df_path = Path(mother_df)
        logger.info('Received string as mother_df, will read file at {}'.format(read_df_path))
        mother_df = get_csv(read_df_path)
        del read_df_path

    if can_have_new_columns:
        logger.warning('can_have_new_columns is not currently implemented')

    df = mother_df.copy()
    to_append = []

    logger.debug('Index of new df are {}'.format(new_df))
    new_indexes = set(new_df.index)
    matched_new_locs = set()

    key_match = 'pr_number'
    unmatched_mother_locs = set()

    for loc, row in df.iterrows():
        match_ix = (new_df[key_match] == row[key_match]).fillna(False)
        _n_match = sum(match_ix)
        if _n_match > 1:
            logging.critical('Row at loc {} found duplicates'.format(loc))
            logging.critical('Row {}'.format(row))
            logging.critical('Duplicates {}'.format(new_df[match_ix]))
            if drop_duplicates:
                logging.info('Dropping duplicate')
                continue
            else:
                raise NotImplementedError('Only drop duplicates when encountered')
        elif _n_match == 0:
            continue
            unmatched_mother_locs.add(loc)
        else:
            # Replace values on columns
            matched_element = new_df.loc[match_ix].iloc[0]
            for c in columns:
                if pd.isna(row[c]) and not overwrite_columns:
                    logger.info('Row {}: not updating column {} with value {} because it is populated'.format(loc, c, row[c]))
                else:
                    df.loc[loc, c] = matched_element[c]
                    matched_new_locs.add(matched_element.name)

    unmatched_new_locs = new_indexes - matched_new_locs
    to_append = [new_df.loc[unmatched_loc] for unmatched_loc in unmatched_new_locs]
    logger.info('Will add {} new references to the end of the dataframe because they were not found.'.format(len(unmatched_new_locs)))
    logger.debug('Locations to append: {}'.format(' '.join((str(un) for un in unmatched_new_locs))))

    logger.info('Kept {} references in mother dataframe intact'.format(len(unmatched_mother_locs)))
    _df = pd.concat([df, pd.DataFrame(to_append)], ignore_index=True)
    return _df

@cli.command()
@click.argument('mother', type=click.Path(dir_okay=False, exists=True))
@click.argument('new', type=click.Path(dir_okay=False, exists=True))
@click.argument('columns', nargs=-1)
@click.option('--output-file', default=None)
@click.option('--overwrite-columns', is_flag=True)
@click.option('--use-new-columns', is_flag=True)
def merge(mother, new, columns, overwrite_columns, use_new_columns, output_file):
    logger.info('Using columns {}'.format(columns))
    df = merge_to_mother_dataframe(new_df=new, mother_df=mother, columns=columns, overwrite_columns=overwrite_columns, can_have_new_columns=use_new_columns)
    if output_file:
        if output_file == '--':
            import sys
            df.to_csv(sys.stdout, index=False)
            exit(0)

        fpath = Path(output_file)
        def write():
            df.to_csv(fpath, index=False)
            logger.info('Wrote to {}'.format(fpath))

        if fpath.exists():
            if click.confirm('Output {} exits. Override?..'.format(fpath)):
                write()
        else:
            write()
    else:
        logger.info('No output file')


if __name__ == "__main__":
    cli()
