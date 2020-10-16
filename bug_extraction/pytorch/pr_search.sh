#!/usr/bin/env bash
# This script is meant to be called the following way:
# PYTORCH_DIR=/path/to/pytorch /this/script/location <PR_NUMBER> <PR_NUMBER> ... <PR_NUMBER>

# It accepts infinte number of Pull Request numbers for PyTorch and calls the script
# `pr_commit_search.sh` located right next to this.
# This script is optional, it is merely a wrapper to do multiple calls AND write the
# output.

# Output will be in the Current Working Directory where you call the script
# aka $PWD when you call it.

pr_script_location="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )/pr_commit_search.sh"
PYTORCH_DIR=${PYTORCH_DIR:?Please input a PyTorch Directory by modifying this file or passing as a env variable.}
pytorch_dir=$(readlink -f ${PYTORCH_DIR})
ALL_PR=( $@ )
OUTPUT_DIR="./out/pytorch/diffs"
# echo "Got ${#ALL_PR[@]} arguments"

mkdir -p $OUTPUT_DIR

for pr in ${ALL_PR[*]}; do
    output_file="$OUTPUT_DIR/pr_${pr}.txt"
    fp=$(readlink -f $output_file)
    # Since we might be executing git from another location than the repository, we have to
    # indicate to git to use the GIT_DIR repository. Note that it needs to end with .git
    GIT_DIR="$pytorch_dir/.git" $pr_script_location --strict --no-color $pr|tee $output_file
    echo "Saved file output to $output_file"
    echo "============="
done
