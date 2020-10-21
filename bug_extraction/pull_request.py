import os
import click
import logging
import github
import requests
from pathlib import Path
import json
import pickle
import pandas as pd
import data_utils
from github import Github, Repository, GitRelease
import repositories

logging.basicConfig(level=logging.INFO)

def get_client():
    from dotenv import load_dotenv
    load_dotenv()
    return Github(os.environ['GITHUB_PAT'])

@click.group()
def cli():
    pass

def get_local_pr(input_dir, pull_request_number, use_json):
    """Get a pull request information JSON file using local directory."""
    if isinstance(input_dir, str):
        input_dir = Path(input_dir)
    ext, file_mode = ('json', 'r') if use_json else ('pkl', 'rb')
    pr_file = input_dir / '{}.{}'.format(pull_request_number, ext)
    logging.debug('Reading from file {}'.format(pr_file))
    if use_json:
        with open(pr_file, file_mode) as p:
            return json.load(p)
    else:
        with open(pr_file, file_mode) as p:
            # Raw API response is second object
            return pickle.load(p)[1]

@cli.command()
@click.argument('pull-request-number', type=int)
@click.option('--framework', type=click.Choice(['PyTorch'], case_sensitive=False), default='PyTorch')
@click.option('--use-json/--use-pickle', default=True)
@click.option('--local/--fetch', default=True)
@click.option('--write/--no-write', default=True)
def fetch_diffs(pull_request_number, framework, use_json, local, write):
    """Fetches patch and diffs for the supplied pull request.
    
    Reads the local directory for the framework in order to do so.

    Note that the patch and diff are based on the branching commit, which
    might be different than the commit from where it is integrated.
    """
    root_path = Path('out').joinpath(framework.lower())
    p_input_dir = root_path / 'pull_requests'

    base_branch, buggy_commit, patch_url, diff_url = None, None, None, None
    if local:
        obj = get_local_pr(p_input_dir, pull_request_number, use_json)
        if use_json:
            base_branch, buggy_commit = obj['base']['ref'], obj['base']['sha']
            patch_url, diff_url = obj['patch_url'], obj['diff_url']
            logging.info('[{}] Commit based from branch "{}" at commit "{}"'.format(pull_request_number, base_branch, buggy_commit))
            logging.info('[{}] Patch url: {}'.format(pull_request_number, patch_url))
            logging.info('[{}] Diff  url: {}'.format(pull_request_number, diff_url))
        else:
            pass
    else:
        raise NotImplementedError('Fetching information from GitHub remote is not implemented yet.')

    # Get patch url and diff url
    patch_req, diff_req = requests.get(patch_url), requests.get(diff_url)
    patch_obj, diff_obj = patch_req.text, diff_req.text

    if int(patch_req.status_code) != 200:
        raise Exception("Failed to get patch. Expected status code {} got {}".format(200, patch_req.status_code))
    elif int(diff_req.status_code) != 200:
        raise Exception("Failed to get diff. Expected status code {} got {}".format(200, diff_req.status_code))

    if write:
        logging.debug('[{}] Writing local files to root dir {}'.format(pull_request_number, p_input_dir))
        patch_path, diff_path = p_input_dir / f'{pull_request_number}.patch', p_input_dir / f'{pull_request_number}.diff'
        with open(patch_path, 'w') as f:
            logging.info('[{}] Writing patch info to {}'.format(pull_request_number, patch_path))
            f.write(patch_obj)
        with open(diff_path, 'w') as f:
            logging.info('[{}] Writing diff info to {}'.format(pull_request_number, diff_path))
            f.write(diff_obj)

@cli.command()
@click.argument('pull-request-number', type=int)
@click.option('--framework', type=click.Choice(['PyTorch'], case_sensitive=False), default='PyTorch')
@click.option('--write/--no-write', default=True)
@click.option('--out-pickle', is_flag=True)
def fetch_single(pull_request_number, framework, write, out_pickle):
    """Downloads a single Pull Request identified by its number."""
    logging.info('Want framework {}'.format(framework))
    logging.info('Pull Request number is {}'.format(pull_request_number))

    root_path = Path('out').joinpath(framework.lower())
    p_output_dir = root_path / 'pull_requests'
    p_output_dir.mkdir(exist_ok=True)
    pr = fetch_and_save_pr(framework, pull_request_number, output_dir=p_output_dir, write=write, out_pickle=out_pickle)
    pr_id, pr_merged = pr.id, pr.merged
    logging.info('Pull Request was merged: {}'.format(pr_merged))


def fetch_and_save_pr(framework, pull_request_number, output_dir, write=True, out_pickle=True):
    framework_obj = repositories.get_repo(framework)
    p_output_dir = Path(output_dir)
    github_link = framework_obj['link']

    logging.debug('Fetching github repo from {}'.format(github_link))
    repo = client.get_repo(github_link)
    pr = repo.get_pull(pull_request_number)

    if write:
        fp = p_output_dir / '{}.json'.format(pull_request_number)
        with open(fp, 'w') as p:
            json.dump(pr.raw_data, p)
            logging.debug('Wrote pull request {} to {}'.format(pull_request_number, fp))

        if out_pickle:
            fp = p_output_dir / '{}.pkl'.format(pull_request_number)
            with open(fp, 'wb') as p:
                client.dump(pr, p)
                logging.debug('Wrote pull request {} to {}'.format(pull_request_number, fp))
    else:
        logging.debug('Not saving pull {} request to local cache'.format(pull_request_number))

    return pr

def get_or_fetch_pr(framework, pull_request_number, cache_dir, write=True, force_fetch=False, **kwargs):
    framework_obj = repositories.get_repo(framework)
    def fetch():
        pr = fetch_and_save_pr(framework, pull_request_number, output_dir=cache_dir, write=True, out_pickle=True)
        return pr.raw_data
    try:
        if force_fetch:
            logging.info('Force fetching pull request')
            return fetch()
        logging.debug('Trying local pr')
        pr = get_local_pr(pull_request_number=pull_request_number, input_dir=cache_dir, **kwargs)
        return pr
    except FileNotFoundError as err:
        logging.debug('Pull request file not found, using fetch method')
        return fetch()
    except json.decoder.JSONDecodeError as err:
        logging.debug('Pull request file had JSON error, using fetch method', extra=err)
        return fetch()


@cli.command()
@click.option('--framework', type=click.Choice(['PyTorch'], case_sensitive=False), default='PyTorch')
@click.option('--pull-request-file', '-f', type=click.Path(exists=True, dir_okay=False))
@click.option('--write/--no-write', default=True)
@click.option('--force-fetch', is_flag=True)
def fetch_pull_request_names(framework, pull_request_file, write, force_fetch):
    """Outputs a CSV with the title of the Pull Request information inserted.
    
    Needs an input file, usually concat.csv, to iterate through the
    rows.
    Will fetch or read cache depending on the parameters.
    """
    df = data_utils.get_csv(pull_request_file)
    root_path = Path('out').joinpath(framework.lower())
    p_output_dir = root_path / 'processed_v2'
    p_pull_requests_dir = root_path / 'pull_requests'

    def show_prog_item(t):
        return f"Pull Request {t[0] if t else 'unknown'}"

    with click.progressbar(df.iterrows(), label="Finding Pull Requests",
                            item_show_func=show_prog_item,
                            length=df.shape[0],
                            show_percent=True,
                            show_eta=False,
                            show_pos=True) as bar:
        for i, row in bar:
            pr_number = row['pr_number']
            if pd.isna(pr_number):
                logging.debug('PR number is None, not treating it')
                continue
            pr_number = int(pr_number)
            logging.debug('Treating PR {}'.format(pr_number))
            try:
                pr = get_or_fetch_pr(framework, pr_number, cache_dir=p_pull_requests_dir, use_json=True, write=True, force_fetch=force_fetch)
                df.loc[i, 'pr_name'] = pr['title']
            except github.GithubException as gh_err:
                logging.warning('Could not get data from github for Pull Request {}'.format(pr_number))
                continue

    if write:
        p_out_file = p_output_dir / 'concat_updated.csv'
        logging.info('Writing to {}'.format(p_out_file))
        # Reindex to put the order of the columns ok
        df.to_csv(p_out_file, index=False)
    logging.info('Fetched information for all pull requests ({})'.format(len(df)))
            
if __name__ == "__main__":
    client = get_client()
    cli()
