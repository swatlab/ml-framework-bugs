import os
import json
import pandas as pd
from pathlib import Path
from time import sleep
import datetime

import requests
from dotenv import load_dotenv

BASE_ISSUES_DIR = Path("data/issues/")


def get_max_pages_from_header(header):
    """
    Parses the header of a request result to obtain the number of issues pages
    
    parameters: the request result's header
    """
    from urllib.parse import urlparse, parse_qs
    link_header = header.get("Link")
    
    if link_header is None:
        return None
    
    # separate the header into fields
    # iterate through all fields to find the last page using the keyword 'rel="last"'
    pages = header["Link"].split(",")
    last_page = next((x for x in pages if 'rel="last"' in x))
    
    # clean up the uri of the last page (remove “;”, “<” and “>”)
    last_page_uri = last_page.split(";")[0].strip().lstrip("<").rstrip(">")
    
	# parse the uri to get the last page
    last_page_number = int(parse_qs(urlparse(last_page_uri).query)["page"][0])
    
    return last_page_number


def get_issues(framw_row, label = None):
    """
    For one framework, checks if labels are needed then makes requests.
    Uses a incremental page number to get all the requests.
    
    parameters :
        framw_row : a row in the frameworks csv
        labal : the wanted label(s) for the framework
    """
    issues_uri = framw_row["apiUri"]
    params = { "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "state": "all", 
               "per_page": 100}
    
    
    if label:
        assert isinstance(label, str)
        params['labels'] = label
        
    # Make request one request only.
    # it is to obtain the number of pages before making all requests
    resp = requests.get(issues_uri, params = params)
    js_resp = resp.json()
    max_pages = get_max_pages_from_header(resp.headers)
    
    print("max pages : ", max_pages)
    
    # If no pages are returned by the Link header
    if max_pages is None:
        return [js_resp]
    
    # Check that the type of the response is correct
    responses = js_resp
    assert isinstance(responses, list)
    
    # Iterate from 2nd page to number of max pages
    for i in range(2, max_pages+1):
        
        # Infinite loop to re-launch request. Sometimes, the server blocks the connection
        # because of too many requests.
        while True:
            try:
                # make request andsave result in responses
                params["page"] = i
                resp = requests.get(issues_uri, params = params)
                print("Get page ", i,framw_row['framework'], " at ", datetime.datetime.now())
                js_resp = resp.json()
                responses.extend(js_resp)
            except (ConnectionError, requests.exceptions.ChunkedEncodingError):
                print("connection lost at ", datetime.datetime.now(), ". Retrying in 10 seconds.")
                sleep(10)
                continue
            break
    return responses


def clean_issue_label_name(label):
    """
    Removes OS unsafe characters ":" and "/" in the label name
    
    parameters:
        label : litteral label name as used in issues repo
    """
    return label.replace(":", "_").replace("/", "_")


def main():
    framework_label_mapping = {}# "TensorFlow": ["type:bug/performance", "prtype:bugfix"] }
    framework_df = pd.read_csv("framework_dataframe.csv")
    
    BASE_ISSUES_DIR.mkdir(parents=True, exist_ok=True)
    for i, row in framework_df.iterrows():
        framw_name = row['framework']
        label_names = framework_label_mapping.get(framw_name, [None])
        print(framw_name)
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
    main()
    write_closed_issues_to_csv()
