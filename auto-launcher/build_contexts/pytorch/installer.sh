#!/usr/bin/env bash

if [ ! -e "commits.txt" ]; then
  echo "File commits.txt is not found. Please create a file with each line containing a version you would like to build"
  exit 1
fi
if [ -z ${CUDA_VERSION+x} ]; then
  echo "CUDA_VERSION needs to be set"
  exit 1
elif [[ "$CUDA_VERSION" =~ "9.0" ]]; then
  echo "Building for CUDA $CUDA_VERSION"
elif [[ "$CUDA_VERSION" =~ "10.0" ]]; then
  echo "Building for CUDA $CUDA_VERSION"
else
  echo "Please set env CUDA_VERSION"
  exit 1
fi
BUILD_DIR="/builds/$CUDA_VERSION"

mkdir -p "$BUILD_DIR"

IFS=$'\n' read -d '' -r -a commits < commits.txt
filesindir=$(ls $BUILD_DIR/*.whl)
for c in "${commits[@]}"; do
  echo "Checking files for commit $c"
  possiblefn=""
  if [[ "$filesindir" =~ "$c" ]]; then
    echo "File found. Skipping..."
    continue
  else
    echo "Not found"
  fi

  LOGFILE="$c.output"
  echo 'Building at:'
  git show $c --oneline --no-patch
  if [ ! "$?" -eq 0 ]; then
    exit 1
  fi

  git checkout $c
  git submodule update --init
  CMAKE_PREFIX_PATH=${CONDA_PREFIX:-"$(dirname $(which conda))/../"}
  # Disable MKLDNN since it weirdly breaks builds
  # python setup.py bdist_wheel
  USE_MKLDNN=0 USE_CUDA=1 python setup.py bdist_wheel | tee "$BUILD_DIR/$LOGFILE"

  cp --update -t "$BUILD_DIR" dist/*
done
