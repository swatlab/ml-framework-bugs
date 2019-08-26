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
    
    return :
        number of max page (int)
    
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
    
    return :
        json result of all requests
    
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
    
    return :
        cleaned name
    
    parameters:
        label : litteral label name as used in issues repo
    """
    return label.replace(":", "_").replace("/", "_")


def main():
    """
    Uses the frameworks' information in framework_dataframe.csv to request the issues with or 
    without issue label.
    Then, save requests results in json files.
    """
    # Used to specify the wanted label(s) for the specified frameworks.
    framework_label_mapping = {}# "TensorFlow": ["type:bug/performance", "prtype:bugfix"] }
    # Each line is composed of the respective name, Github link, bug repo link, 
    # website URI and API URI of each framework.
    framework_df = pd.read_csv("framework_dataframe.csv")
    
    BASE_ISSUES_DIR.mkdir(parents=True, exist_ok=True)
    
    #Iterate through all frameworks’ info (all csv rows)
    for i, row in framework_df.iterrows():
        
        # get framework name and labels in csv
        framw_name = row['framework']
        label_names = framework_label_mapping.get(framw_name, [None])
        print(framw_name)
        
		# Iterate through all wanted labels
        for label in label_names:
            
            # make requests for issues, issues_for_label is json content
            issues_for_label = get_issues(row, label=label)
            
            # if there is a label, add label name in the filename
            if label:
                safe_label_name = clean_issue_label_name(label)
                label_names = framework_label_mapping.get(framw_name, [None])
                filename = "{}_issues_{}.json".format(row['framework'], safe_label_name) 
            else:
                filename = '{}_issues.json'.format(row['framework'])
            
            # save json content in json file
            with open(BASE_ISSUES_DIR / filename, 'w') as f:
                json.dump(issues_for_label, f)

def write_closed_issues_to_csv(json_issues_path=BASE_ISSUES_DIR):
    """
    Load the json generated in main() and write their content in a csv.
    This method keeps the closed issues and doesn't write the open issues
    """
    CLOSED_ISSUES_DIR = Path('data/closed_issues/')
    CLOSED_ISSUES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Iterate through all json files in json_issues_path
    for jf in Path.glob(json_issues_path, pattern='*.json'):
        
        # Open and load json
        with open(jf, 'r') as f:
            json_obj = json.load(f)
            
        
        # If extraction was a list of list (backwards compatibility)
        if isinstance(json_obj[0], list):
            flattened = [x for i in json_obj for x in i]
        # Else, it is already flattened
        else:
            flattened = json_obj
        flattened_json_string = json.dumps(flattened) # Dump to string for pandas to read (only accepts str or paths)
        
        # Dump all json in a string
        _df = pd.read_json(flattened_json_string)
        
        # Only select issues that are closed and save them in a csv
        _df = _df[_df['state']=='closed']
        _df.to_csv(CLOSED_ISSUES_DIR / '{}.csv'.format(jf.stem), index=False)

if __name__ == "__main__":
    load_dotenv()
    CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
    CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
    main()
    write_closed_issues_to_csv()
