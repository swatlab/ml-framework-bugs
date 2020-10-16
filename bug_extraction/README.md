# bug_extraction

## Setup
We use [`pip-tools`](https://pypi.org/project/pip-tools/) to manage dependencies. Follow their instructions and run `pip-sync`
1. Create `.env` file with key `GITHUB_PAT`

# Phases
## 1: Fetching releases and bug fixes from PyTorch
### Goal
- Fetch releases notes into `out/pytorch/raw/pytorch_<version>.md`
- Attempt at parsing the release notes for bug fixes via regular expressions. Bug fixes are accumulated into a dataframe and placed in `out/pytorch/processed/pytorch_<version>.{csv|json}`
### Procedure
```bash
python pytorch_release_extract.py
```
### Notes
_This process will leave empty values in the dataframes, for the bug fixes that are detected (in the same region) not parseable._
**Some more (manual work) is needed to parse the bug fixes from old releases (pre-v1.x) and release candidates (`rcX`).

## 2: Filtering bug fixes for parseable ones
### Goal
- Create a new dataframe with the bugs that have a Pull Request number on them that was parsed.
- Create a concatenated dataframe will all the bugs in it
```bash
python pytorch_process_release.py --framework pytorch [--concatenate]
```
With the concatenate option, this will create the file `out/pytorch/processed_v2/concat.csv`
### Notes
The output from this step goes into the document for Mother CSV.


## WIP: 3: Getting Pull Request information with Pull Request number
### Goal
- Get the commits on which we will build the versions for each bug (which should have a pull request associated)
### Procedure
```bash
python pytorch_pull_request_commits.py locally --git-dir /path/path/pytorch --pull-request-file out/pytorch/processed_v2/concat.csv --bash-script-file pytorch/pr_commit_search.sh --parallel
```
### Notes
This will create files under `out/pytorch/diffs/`


# Things to better
1. Use a class for each bug extractor instead of files

# Disclaimer
There is much work to be done to parse bug fixes. The regex still needs fine-tuning. Idea:
- Use `re.search` to find markdown links
