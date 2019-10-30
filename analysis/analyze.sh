#!/usr/bin/env bash

DUMP_EXPERIMENTS_TO_RUN="experiments_to_run.txt"
if [ -f "$DUMP_EXPERIMENTS_TO_RUN" ]; then
    echo "Dump of experiments to run file already present, deleting..."
    rm --preserve-root "$DUMP_EXPERIMENTS_TO_RUN"
fi
# Please put this file in the directory containing _data or set variable DIR
# to point to correct path, ex: set DIR=/path/to/volume
# ex: /docker/volumes/results
# If you do, remove the declaration a bit below
DIR="/docker/volumes/results"

# Set DIR to current directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

function colorprint {
    echo "$(tput setaf $1)${@:2}$(tput sgr0)"
}

# Definitions
COLORRED="1"
COLORGREEN="2"
COLORYELLOW="3"
COLORBLUE="4"
COLORPURPLE="5"

# TODO: Remove the _data so that we can point to an arbitrary directory
# Client side parameters
# NB: We can let bash variable expansion deal with listing instead of using ls
PARAM_FILES=( $DIR/_data/pyt_*.parameters.log )
echo "There are ${#PARAM_FILES[@]} param files"
# Server side files
METRICS_FILES=( $DIR/_data/pyt_*_metrics.log )
echo "There are ${#METRICS_FILES[@]} server metrics files"


let i=0
let diff_count=0
let no_diff_count=0

# for fff in "${PARAM_FILES[@]}"; do
for fff in "${METRICS_FILES[@]}"; do
    # echo "Treating file $fff"
    colorprint "$COLORYELLOW" "[$i] Treating file ${fff##*/}"

    file_type="${fff##*_}"
    # Uncomment for client-side:
    # file_type="${file_type%.parameters.log}"
    # Uncomment for server-side:
    file_type=$(sed -r 's/.*(buggy|corrected).*/\1/' <<< "${fff}")
    colorprint "$COLORYELLOW" "  File type first is $file_type"

    unset complementary_file file_name complementary_file_name
    if [ "$file_type" = "corrected" ]; then
        complementary_file="${fff/corrected/buggy}"
        # echo "Analyze file $fff and $complementary_file"
    elif [ "$file_type" = "buggy" ]; then
        complementary_file="${fff/buggy/corrected}"
        # echo "Analyze file $fff and $complementary_file"
    else
        colorprint "$COLORRED" "INVALID VALUE ($file_type for variable file_type), should not happen..."
        continue
        # exit 1
    fi

    complementary_file_name=$(basename "$complementary_file")
    file_name=$(basename "$fff")

    # colorprint "$COLORPURPLE" "  diff " "$fff" "$complementary_file"
    diff "$fff" "$complementary_file" > /dev/null
    files_differ="$?"

    if [ "$files_differ" -eq 0 ]; then
        let no_diff_count++
        colorprint "$COLORBLUE" "  No difference between ${fff##*/} and ${complementary_file##*/}"
    else
        let diff_count++
        colorprint "$COLORGREEN" "  Difference found between ${fff##*/} and ${complementary_file##*/}"
        if [ ! -z "$DUMP_EXPERIMENTS_TO_RUN" ]; then
            # Dump experiments that have diff
            echo "${file_name%%_metrics.log}" >> "$DUMP_EXPERIMENTS_TO_RUN"
        fi
    fi

    let i++
done

# TODO: Remove when the processing won't process already processed files
# Divide counts by two because there are two diffs
let diff_count="diff_count/2"
let no_diff_count="no_diff_count/2"

echo ""
colorprint "$COLORYELLOW" "=== SUMMARY ==="
colorprint "$COLORYELLOW" "There was $diff_count files with diff and $no_diff_count files with no diff"
colorprint "$COLORYELLOW" "Analyze experiments detailed in $DUMP_EXPERIMENTS_TO_RUN"


