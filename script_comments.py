import json
import os
import pandas as pd
from pathlib import Path
from time import sleep

import requests
from dotenv import load_dotenv

request_uri = {}
BASE_ISSUES_DIR = Path("data/issues/")

def get_comments():
    CLOSED_ISSUES_DIR = Path('data/closed_issues/')
    CLOSED_ISSUES_DIR.mkdir(parents=True, exist_ok=True)
    CLOSED_ISSUES_COMMENTS_DIR = Path('data/closed_issues/comments/')
    CLOSED_ISSUES_COMMENTS_DIR.mkdir(parents=True, exist_ok=True)

    # for each framework csv in directory
    for csv in Path.glob(CLOSED_ISSUES_DIR, pattern='*.csv'):
        closed_issues = pd.read_csv(csv)
        framework_comments = {}
        
        # for each issue in csv
        for i, issue in closed_issues.iterrows():
            # 1) make a first request
            comments_uri = issue["comments_url"] # issues_uri + issue['number'] + "/comments"
            params = { "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, 
                       "per_page": 100}
            
            resp = requests.get(comments_uri, params = params)
            js_resp = resp.json()
            
            # 2) calculate number of segmentation pages
            max_pages = get_max_pages_from_header(resp.headers)
            
            if max_pages is None: # No pages are returned by the Link header
                max_pages = 0
            
            # 3) get all issues comments (comments that are on segm pages)
            all_issue_comments = js_resp
            
            assert isinstance(all_issue_comments, list)
            # for each segmentation page
            for i in range(2, max_pages+1):
                while True:
                    try:
                        params["page"] = i
                        resp = all_issue_comments.get(comments_uri, params = params)
                        js_resp = resp.json()
                        all_issue_comments.extend(js_resp)
                    except SomeSpecificException:
                        continue
                    break
            
            # 4) write issue number and comments in a dict
            #    that is unique to each framework
            framework_comments[issue.number] = all_issue_comments
                
            print(framework_comments[i])
        
        # 5) write dict in a json
        with open(CLOSED_ISSUES_COMMENTS_DIR / '{}_comments.json'.format(csv.stem), 'w') as f:
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

def clean_issue_label_name(label):
    return label.replace(":", "_").replace("/", "_")

def write_closed_issues_to_csv(json_issues_path=BASE_ISSUES_DIR):
    CLOSED_ISSUES_DIR = Path('data/closed_issues/')
    CLOSED_ISSUES_DIR.mkdir(parents=True, exist_ok=True)

    for jf in Path.glob(json_issues_path, pattern='*.json'):
        with open(jf, 'r') as f:
            json_obj = json.load(f)
        if isinstance(json_obj[0], list):
            # If extraction was a list of list (backwards compatibility)
            flattened = [x for i in json_obj for x in i]
        else:
            flattened = json_obj
        flattened_json_string = json.dumps(flattened) # Dump to string for pandas to read (only accepts str or paths)

        _df = pd.read_json(flattened_json_string)
        _df = _df[_df['state']=='closed']
        _df.to_csv(CLOSED_ISSUES_DIR / '{}.csv'.format(jf.stem), index=False)

if __name__ == "__main__":
    load_dotenv()
    CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
    CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
    get_comments()
    # write_closed_issues_to_csv()
