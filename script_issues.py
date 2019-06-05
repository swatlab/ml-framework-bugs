import json
import pandas as pd
import requests

CLIENT_ID = "***REMOVED***"
CLIENT_SECRET = "***REMOVED***"
#

def get_issues(project_row, labels = None):
    issues_uri = project_row["apiUri"]
    params = { "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "state": "all"}
    if labels:
        assert isinstance(labels, list)
        params['labels'] = ",".join(labels)
    resp = requests.get(issues_uri, params = params)
    print(resp.request.url)
    js_resp = resp.json()
    return js_resp

def main():
    framework_label_mapping = { "TensorFlow": ["type:bug/performance", "prtype:bugfix"] }
    df = pd.read_csv("test.csv")
    for i, row in df.iterrows():
        label_names = framework_label_mapping.get(row['framework'])
        issues = get_issues(row, labels = label_names)
        filename = "{}_issues_{}.json".format(row['framework'], len(label_names)) if label_names else '{}_issues.json'.format(row['framework'])
            
        with open(filename, 'w') as f:
            json.dump(issues, f)

if __name__ == "__main__":
    session = requests.Session()
    main()
    session.close()
