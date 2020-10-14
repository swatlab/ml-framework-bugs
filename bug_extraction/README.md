# bug_extraction

## Setup
We use [`pip-tools`](https://pypi.org/project/pip-tools/) to manage dependencies. Follow their instructions and run `pip-sync`
1. Create `.env` file with key `GITHUB_PAT`

## Getting "raw" information from Github
1. Run `python pytorch_release_extract.py`, this will download release values to `out/raw/` and preprocess some data in `out/processed/`
1. Run `python pytorch_process_release.py --framework pytorch [--concatenate]`

# Things to better
1. Use a class for each bug extractor instead of files

# Disclaimer
There is much work to be done to parse bug fixes. The regex still needs fine-tuning. Idea:
- Use `re.search` to find markdown links
