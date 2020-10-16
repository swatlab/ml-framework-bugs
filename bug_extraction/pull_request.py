import os
import click
import logging
import github
import requests
from pathlib import Path

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
    ext, file_mode = ('json', 'r') if use_json else ('pkl', 'rb')
    pr_file = input_dir / '{}.{}'.format(pull_request_number, ext)
    logging.info('Reading from file {}'.format(pr_file))
    if use_json:
        import json
        with open(pr_file, file_mode) as p:
            return json.load(p)
    else:
        import pickle
        with open(pr_file, file_mode) as p:
            # Raw API response is second object
            return pickle.load(p)[1]

@cli.command()
@click.argument('pull-request-number', type=int)
@click.option('--framework', type=click.Choice(['PyTorch'], case_sensitive=False), default='PyTorch')
@click.option('--use-json/--use-pickle', default=True)
@click.option('--local/--fetch', default=True)
@click.option('--write/--no-write', default=True)
def extract_commits(pull_request_number, framework, use_json, local, write):
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
@click.option('--raw-only', is_flag=True)
def pull_request(pull_request_number, framework, raw_only, write):
    logging.info('Want framework {}'.format(framework))
    logging.info('Pull Request number is {}'.format(pull_request_number))

    root_path = Path('out').joinpath(framework.lower())
    p_output_dir = root_path / 'pull_requests'
    p_output_dir.mkdir(exist_ok=True)

    framework_obj = repositories.get_repo(framework)

    if raw_only:
        import requests
        logging.info('Using raw request')
        headers = {'Authorization': 'token {}'.format(os.environ['GITHUB_PAT'])}
        endpoint = '{}/pulls/{}'.format(framework_obj['api_full_url'], pull_request_number)

        logging.debug('Requesting endpoint {}'.format(endpoint))
        r = requests.get(endpoint, headers=headers)
        if int(r.status_code) != 200:
            logging.warning('Request return unexpected status code {}'.format(r.status_code))
            raise Exception('Wrong status code, expected 200 got {}'.format(r.status_code))
        response = r.json()
        if write:
            import json
            fp = p_output_dir / '{}.json'.format(pull_request_number)
            with open(fp, 'w') as p:
                json.dump(response, p)
                logging.info('Wrote pull request {} to {}'.format(pull_request_number, fp))
    else:
        logging.info('Using PyGithub request')
        github_link = framework_obj['link']

        logging.debug('Fetching github repo from {}'.format(github_link))
        repo = client.get_repo(github_link)
        pr = repo.get_pull(pull_request_number)

        pr_id, pr_merged = pr.id, pr.merged
        logging.info('Pull Request was merged: {}'.format(pr_merged))

        if write:
            fp = p_output_dir / '{}.pkl'.format(pull_request_number)
            with open(fp, 'wb') as p:
                client.dump(pr, p)
                logging.info('Wrote pull request {} to {}'.format(pull_request_number, fp))

if __name__ == "__main__":
    client = get_client()
    cli()
