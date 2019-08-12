import csv
import json
import os
import pandas as pd
from pathlib import Path
from time import sleep
import datetime

import requests
from dotenv import load_dotenv

import argparse

PARSER = argparse.ArgumentParser()
PARSER.add_argument('--use-pat', '--use-personal-access-token',
                    action='store_true',
                    help='Use a personal access token instead of client id and secret', )
PARSER.add_argument('--use-request-session', action='store_true',
                    help='Use a single request session for all requests')
request_uri = {}

CLOSED_ISSUES_COMMENTS_JSON_DIR = Path('data/closed_issues/comments/json/')

def wait_for_time_and_continue(resp):
    remaining_requests = int(resp.headers.get('X-RateLimit-Remaining', -1))
    # Retry if the header is not present for whatever reason
    if remaining_requests == -1:
        return True
    if resp.status_code == 403 and remaining_requests == 0:
        reset_time = int(resp.headers.get('X-RateLimit-Reset', -1))
        if reset_time == -1:
            # If no reset time was set wait an hour
            reset_time = datetime.datetime.now().timestamp() + 3600
        # Apparently it's not utcnow....weird
        wait_delta = reset_time - datetime.datetime.now().timestamp()
        wait_delta = int(wait_delta) + 1
        print('RateLimit achieved. Waiting {} seconds.'.format(wait_delta))
        sleep(wait_delta)
        return True
    else:
        return False


def get_comments(base_request_params, request_auth, use_request_session=False):
    CLOSED_ISSUES_DIR = Path('data/closed_issues/')
    CLOSED_ISSUES_DIR.mkdir(parents=True, exist_ok=True)
    CLOSED_ISSUES_COMMENTS_JSON_DIR.mkdir(parents=True, exist_ok=True)

    framework_csvs = list(f for f in Path.glob(CLOSED_ISSUES_DIR, pattern='*.csv'))
    n_frameworks = len(framework_csvs)
    if use_request_session:
        s = requests.Session()
    http_caller = s if use_request_session else requests

    # for each framework_csv in directory
    for framework_counter, csv in enumerate(framework_csvs):
        print("[{}/{}] {}".format(framework_counter, n_frameworks, csv.stem))
        closed_issues = pd.read_csv(csv)
        framework_comments = {}
        
        framework_cache_dir = CLOSED_ISSUES_COMMENTS_JSON_DIR / '.cache_{}'.format(csv.stem)
        framework_cache_dir.mkdir(exist_ok=True)
        n_issues = len(closed_issues)

        # for each issue in csv
        for issue_counter, issue in closed_issues.iterrows():
            # 1) make a first request
            # issues_uri + issue['number'] + "/comments"
            comments_uri = issue["comments_url"]
            params = base_request_params
            _cache_file_name = "{}_{}.json".format(csv.stem, issue.number)
            if (framework_cache_dir / _cache_file_name).exists():
                with open(framework_cache_dir / _cache_file_name, 'r') as jf:
                    framework_comments[issue.number] = json.load(jf)
                    print("{} [{}/{}] {} Loaded from cache issue {}".format(datetime.datetime.now(), issue_counter, n_issues, csv.stem, issue.number))
                continue

            # If response was not found in cache query the first page
            while True:
                try:
                    print("{} [{}/{}] {} Getting issue {} page 1".format(datetime.datetime.now(), issue_counter, n_issues, csv.stem, issue.number))
                    resp = http_caller.get(comments_uri, params=params, auth=request_auth)
                    if wait_for_time_and_continue(resp):
                        continue # Previous request failed so we retry
                    js_resp = resp.json()
                except (ConnectionError, requests.exceptions.ChunkedEncodingError):
                    print("internet connection lost, retrying in 10s.")
                    sleep(10)
                    continue
                except (requests.exceptions.SSLError):
                    print("SSL Max entries exceeded, retrying in 100s.")
                    sleep(100)
                    continue
                break

            # 2) calculate number of segmentation pages
            # max_pages = get_max_pages_from_header(resp.headers)
            next_page_url = get_next_url_from_header(resp.headers)
            # if max_pages is None:  # No pages are returned by the Link header
            #     max_pages = 0

            # print("max pages : ", max_pages+1)

            # 3) get all issues comments (comments that are on segm pages)
            all_issue_comments = js_resp

            if not isinstance(all_issue_comments, list):
                print("all_issue_comments not a list, instead type {}".format(type(all_issue_comments)))
                print(all_issue_comments)
                exit()
            assert isinstance(all_issue_comments, list)
            
            # for each segmentation page
            # for page_counter in range(2, max_pages+1):
            page_counter = 0
            while next_page_url is not None:
                params["page"] = page_counter
                while True:
                    try:
                        print("{} [{}/{}] {} Getting issue {} page {}".format(datetime.datetime.now(), issue_counter, n_issues, csv.stem, issue.number, page_counter))
                        resp = http_caller.get(comments_uri, params=params, auth=request_auth)
                        if wait_for_time_and_continue(resp):
                            continue # Previous request failed so we retry
                        js_resp = resp.json()
                        next_page_url = get_next_url_from_header(resp.headers)
                        all_issue_comments.extend(js_resp)
                    except (ConnectionError, requests.exceptions.ChunkedEncodingError):
                        print("internet connection lost, retrying in 10s.")
                        sleep(10)
                        continue
                    except (requests.exceptions.SSLError):
                        print("SSL Max entries exceeded, retrying in 100s.")
                        sleep(100)
                        continue
                    page_counter += 1
                    break

            # Only write once we have all pages for the issue
            with open(framework_cache_dir / _cache_file_name, 'w') as jf:
                json.dump(all_issue_comments, jf)

            # 4) write issue number and comments in a dict
            #    that is unique to each framework
            framework_comments[issue.number] = all_issue_comments

        # 5) write dict in a json
        with open(CLOSED_ISSUES_COMMENTS_JSON_DIR / '{}_comments.json'.format(csv.stem), 'w') as f:
            json.dump(framework_comments, f)

def get_next_url_from_header(header):
    from urllib.parse import urlparse, parse_qs
    link_header = header.get("Link")
    if link_header is None:
        return None
    pages = header["Link"].split(",")
    next_page = next((x for x in pages if 'rel="next"' in x), None)
    if next_page is None:
        return None
    next_page_uri = next_page.split(";")[0].strip().lstrip("<").rstrip(">")
    return next_page_uri

def get_max_pages_from_header(header):
    from urllib.parse import urlparse, parse_qs
    link_header = header.get("Link")
    if link_header is None:
        return None
    pages = header["Link"].split(",")
    try:
        last_page = next((x for x in pages if 'rel="last"' in x))
    except StopIteration as sie:
        print("StopIteration error:", sie)
        print(link_header)
        print(pages)
        raise sie
    last_page_uri = last_page.split(";")[0].strip().lstrip("<").rstrip(">")
    last_page_number = int(parse_qs(urlparse(last_page_uri).query)["page"][0])
    return last_page_number


def write_closed_issues_comments_to_csv(json_issues_path=CLOSED_ISSUES_COMMENTS_JSON_DIR):
    CLOSED_ISSUES_COMMENTS_CSV_DIR = Path('data/closed_issues/comments/csv/')
    CLOSED_ISSUES_COMMENTS_CSV_DIR.mkdir(parents=True, exist_ok=True)

    for jf in Path.glob(json_issues_path, pattern='*.json'):
        with open(jf, 'r') as f:
            json_obj = json.load(f)

        if isinstance(json_obj, dict):
            _df = pd.DataFrame.from_dict(json_obj, orient='index')
            _df.transpose()
            _df.to_csv(CLOSED_ISSUES_COMMENTS_CSV_DIR /
                       '{}.csv'.format(jf.stem), index=False)
        elif isinstance(json_obj[0], list):
            # If extraction was a list of list (backwards compatibility)
            flattened = [x for i in json_obj for x in i]
            # Dump to string for pandas to read (only accepts str or paths)
            flattened_json_string = json.dumps(flattened)
            _df = pd.read_json(flattened_json_string)
            _df.to_csv(CLOSED_ISSUES_COMMENTS_CSV_DIR /
                       '{}.csv'.format(jf.stem), index=False)
        else:
            flattened = json_obj
            # Dump to string for pandas to read (only accepts str or paths)
            flattened_json_string = json.dumps(flattened)
            _df = pd.read_json(flattened_json_string)
            _df.to_csv(CLOSED_ISSUES_COMMENTS_CSV_DIR /
                       '{}.csv'.format(jf.stem), index=False)


def _make_base_params():
    if ARGS.use_pat:
        return {"per_page": 100}
    else:
        CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
        CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
        if CLIENT_ID == "" or CLIENT_SECRET == "":
            print("CLIENT_ID or CLIENT_SECRET is not defined in the environment variables while using OAuth configuration. Exiting...")
            exit(1)
        return {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
                "per_page": 100}


def _make_auth_params():
    if ARGS.use_pat:
        CLIENT_USER = os.getenv('GITHUB_PERSONAL_ACCESS_USER', "")
        CLIENT_PAT = os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN', "")
        if CLIENT_USER == "" or CLIENT_PAT == "":
            print("CLIENT_USER or CLIENT_PAT is not defined in the environment variables while using PAT configuration. Exiting...")
            exit(1)
        return (CLIENT_USER, CLIENT_PAT)
    else:
        return None


if __name__ == "__main__":
    load_dotenv()
    ARGS = PARSER.parse_args()
    REQUEST_BASE_PARAMS = _make_base_params()
    REQUEST_AUTH_HEADER = _make_auth_params()

    get_comments(base_request_params=REQUEST_BASE_PARAMS,
                 request_auth=REQUEST_AUTH_HEADER,
                 use_request_session=ARGS.use_request_session)
    write_closed_issues_comments_to_csv()
