#!/usr/bin/env bash

# This script is meant to be called the following way:
# GIT_DIR=/path/to/pytorch/.git /this/script/location <PR_NUMBER>

# It accepts a single Pull Request number for PyTorch and verifies
# some of the parent commits.

# Output is made on STDOUT with optional colors
# For scripting use, we suggest the argument:
# --no-color

# The argument --quiet could be used but no output will be shown.
# Only use it to check if a commit is usable

# Note that even with the --quiet option, the return code
# will reflect if there is an error.
# As always, return code 0 means OK and anything
# else indicates an error.

PR_NUMBER=""
USE_COLOR="yes"
QUIET=""

while [[ $# -gt 0 ]]; do
    arg="$1"
    case $arg in
        --strict)
            STRICT="yes"
            shift
            ;;
        --quiet|--silent)
            QUIET="yes"
            shift
            ;;
        --no-color)
            USE_COLOR="no"
            shift
            ;;
        *)
            PR_NUMBER="${1}"
            shift
            ;;
    esac
done

if [ $STRICT = "yes" ]; then
    set -e
fi


log_fn() {
    if [[ ${QUIET} = "yes" ]]; then
        return
    elif [[ ${X_COLOR+x} && ${USE_COLOR} = "yes" ]]; then
        tput setaf $X_COLOR
        echo $@
        tput sgr0
    else
        echo $@
    fi
}

log_fn "GIT_DIR is $GIT_DIR"

log_fn "Getting commit for PR ${PR_NUMBER:?Please provide a commit number}"

matching=( $(git log --grep="#$PR_NUMBER" --format="%H" ) )
n_match=${#matching[@]}
if [ $n_match -eq 0 ]; then
    X_COLOR=1 log_fn "No commit found for $PR_NUMBER. Exiting..."
    exit 1
elif [ $n_match -gt 1 ]; then
    X_COLOR=3 log_fn "Multiple match commits found for $PR_NUMBER (Found $n_match)"
    log_fn ${matching[@]}
    exit 2
else
    X_COLOR=2 log_fn "Found commit for $PR_NUMBER"
    log_fn ${matching[@]}
fi

log_fn "Checking that commit ${matching} is in branch master"
if git merge-base --is-ancestor $matching master; then
    X_COLOR=2 log_fn "Branch master contains $matching"
else
    X_COLOR=1 log_fn "Branch master does not contains $matching"
    exit 3
fi

parentCommit=$(git rev-parse "${matching}^")
log_fn "Parent commit is ${parentCommit}"
