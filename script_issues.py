import json
import pandas as pd
import os
import requests

CLIENT_ID = "***REMOVED***"
CLIENT_SECRET = "***REMOVED***"


def get_issues(project_row, label = None):
    issues_uri = project_row["apiUri"]
    params = { "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "state": "all", 
               "per_page": 100}
    if label:
        assert isinstance(label, str)
        params['labels'] = label
    resp = requests.get(issues_uri, params = params)

    js_resp = resp.json()
    max_pages = get_max_pages_from_header(resp.headers)
    if max_pages is None: # No pages are returned by the Link header
        return [js_resp]
    responses = [js_resp]
    for i in range(2, max_pages+1):
        params["page"] = i
        resp = requests.get(issues_uri, params = params)
        js_resp = resp.json()
        responses.append(js_resp)
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


def main():
    framework_label_mapping = { "TensorFlow": ["type:bug/performance", "prtype:bugfix"] }
    df = pd.read_csv("test.csv")
    
    base_issues_dir.mkdir(parents=True, exist_ok=True)
    for i, row in df.iterrows():
        framw_name = row['framework']
        print("label_names", label_names)
        for label in label_names:
            issues_for_label = get_issues(row, label=label)
            
            safe_label_name = clean_issue_label_name(label)
            if label:
                label_names = framework_label_mapping.get(framw_name, [None])
                filename = "{}_issues_{}.json".format(row['framework'], safe_label_name) 
            else:
                filename = '{}_issues.json'.format(row['framework'])
            
            with open(base_issues_dir / filename, 'w') as f:
                json.dump(issues_for_label, f)


if __name__ == "__main__":
    from pathlib import Path
    base_issues_dir = Path("data/issues/")
    main()
