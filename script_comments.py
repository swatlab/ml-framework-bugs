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
PARSER.add_argument('--use-pat','--use-personal-access-token', 
                    action='store_true',
                    help='Use a personal access token instead of client id and secret', )

request_uri = {}

CLOSED_ISSUES_COMMENTS_JSON_DIR = Path('data/closed_issues/comments/json/')

def get_comments(base_request_params, request_auth):
    CLOSED_ISSUES_DIR = Path('data/closed_issues/')
    CLOSED_ISSUES_DIR.mkdir(parents=True, exist_ok=True)
    CLOSED_ISSUES_COMMENTS_JSON_DIR.mkdir(parents=True, exist_ok=True)

    # for each framework_csv in directory
    for csv in Path.glob(CLOSED_ISSUES_DIR, pattern='*.csv'):
        print(csv.stem)
        closed_issues = pd.read_csv(csv)
        framework_comments = {}
        
        # for each issue in csv
        for i, issue in closed_issues.iterrows():
            # 1) make a first request
            comments_uri = issue["comments_url"] # issues_uri + issue['number'] + "/comments"
            params = base_request_params
            while True:
                try:
                    resp = requests.get(comments_uri, params = params, auth=request_auth)
                    js_resp = resp.json()
                    print("Get page 1, issue ", issue.number, csv.stem, " at ", datetime.datetime.now())
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
            max_pages = get_max_pages_from_header(resp.headers)
            
            if max_pages is None: # No pages are returned by the Link header
                max_pages = 0
            
            print("max pages : ", max_pages+1)
            
            # 3) get all issues comments (comments that are on segm pages)
            all_issue_comments = js_resp
            
            assert isinstance(all_issue_comments, list)
            # for each segmentation page
            for i in range(2, max_pages+1):
                params["page"] = i
                while True:
                    try:
                        resp = all_issue_comments.get(comments_uri, params = params)
                        print("Get page ", i, issue.number,framw_row['framework'], " at ", datetime.datetime.now())
                        js_resp = resp.json()
                        all_issue_comments.extend(js_resp)
                    except (ConnectionError, requests.exceptions.ChunkedEncodingError):
                        print("internet connection lost, retrying in 10s.")
                        sleep(10)
                        continue
                    except (requests.exceptions.SSLError):
                        print("SSL Max entries exceeded, retrying in 100s.")
                        sleep(100)
                        continue
                    break
            
            # 4) write issue number and comments in a dict
            #    that is unique to each framework
            framework_comments[issue.number] = all_issue_comments
        
        # 5) write dict in a json
        with open(CLOSED_ISSUES_COMMENTS_JSON_DIR / '{}_comments.json'.format(csv.stem), 'w') as f:
            json.dump(framework_comments, f)
    
def get_max_pages_from_header(header):
    from urllib.parse import urlparse, parse_qs
    link_header = header.get("Link")
    if link_header is None:
        return None
    pages = header["Link"].split(",")
    last_page = next((x for x in pages if 'rel="last"' in x))
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
            _df.to_csv(CLOSED_ISSUES_COMMENTS_CSV_DIR / '{}.csv'.format(jf.stem), index=False)
        elif isinstance(json_obj[0], list):
            # If extraction was a list of list (backwards compatibility)
            flattened = [x for i in json_obj for x in i]
            flattened_json_string = json.dumps(flattened) # Dump to string for pandas to read (only accepts str or paths)
            _df = pd.read_json(flattened_json_string)
            _df.to_csv(CLOSED_ISSUES_COMMENTS_CSV_DIR / '{}.csv'.format(jf.stem), index=False)
        else:
            flattened = json_obj
            flattened_json_string = json.dumps(flattened) # Dump to string for pandas to read (only accepts str or paths)
            _df = pd.read_json(flattened_json_string)
            _df.to_csv(CLOSED_ISSUES_COMMENTS_CSV_DIR / '{}.csv'.format(jf.stem), index=False)

def _make_base_params():
    if ARGS.use_pat:
        return {"per_page": 100}
    else:
        CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
        CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
        return { "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, 
                "per_page": 100}
def _make_auth_params():
    if ARGS.use_pat:
        CLIENT_USER = os.getenv('GITHUB_PERSONAL_ACCESS_USER')
        CLIENT_PAT = os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')
        return (CLIENT_USER, CLIENT_PAT)
    else:
        return None

if __name__ == "__main__":
    load_dotenv()
    ARGS = PARSER.parse_args()
    print(ARGS)
    REQUEST_BASE_PARAMS = _make_base_params()
    REQUEST_AUTH_HEADER = _make_auth_params()

    get_comments(base_request_params=REQUEST_BASE_PARAMS, request_auth=REQUEST_AUTH_HEADER)
    write_closed_issues_comments_to_csv()
