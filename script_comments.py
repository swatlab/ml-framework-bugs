import os
import json
import pandas as pd
from pathlib import Path

import requests
from dotenv import load_dotenv

request_uri = {}
BASE_ISSUES_DIR = Path("data/issues/")
BASE_COMMENTS_DIR = Path("data/closed_issues/")

def get_issues(framw_row, label = None):
    issues_uri = framw_row["apiUri"]
    comments_uri = issues_uri \ comments
    params = { "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "state": "closed", 
               "per_page": 100}
    if label:
        assert isinstance(label, str)
        params['labels'] = label
    resp = requests.get(issues_uri, params = params)

    js_resp = resp.json()
    max_pages = get_max_pages_from_header(resp.headers)
    if max_pages is None: # No pages are returned by the Link header
        return [js_resp]
    responses = js_resp
    assert isinstance(responses, list)
    for i in range(2, max_pages+1):
        params["page"] = i
        resp = requests.get(issues_uri, params = params)
        js_resp = resp.json()
        responses.extend(js_resp)
    return responses


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

def main():
    framework_label_mapping = { "TensorFlow": ["type:bug/performance", "prtype:bugfix"] }
    framework_df = pd.read_csv("framework_dataframe.csv")
    
    BASE_ISSUES_DIR.mkdir(parents=True, exist_ok=True)
    for i, row in framework_df.iterrows():
        framw_name = row['framework']
        label_names = framework_label_mapping.get(framw_name, [None])
        print("label_names", label_names)
        for label in label_names:
            issues_for_label = get_issues(row, label=label)
            
            if label:
                safe_label_name = clean_issue_label_name(label)
                label_names = framework_label_mapping.get(framw_name, [None])
                filename = "{}_issues_{}.json".format(row['framework'], safe_label_name) 
            else:
                filename = '{}_issues.json'.format(row['framework'])
            
            with open(BASE_ISSUES_DIR / filename, 'w') as f:
                json.dump(issues_for_label, f)

def get_closed_issues(json_issues_path=BASE_ISSUES_DIR):
    CLOSED_ISSUES_DIR = Path('data/closed_issues/')
    CLOSED_ISSUES_DIR.mkdir(parents=True, exist_ok=True)
    kek = 1
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
        closed_issues_urls = _df['url'].values
        request_uri[jf.stem] = [closed_issues_urls]
        

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
    # main()
    get_closed_issues()
    # write_closed_issues_to_csv()
