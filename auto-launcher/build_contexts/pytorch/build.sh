#!/usr/bin/env bash
source /opt/conda/etc/profile.d/conda.sh
conda activate build

if [ "$CONDA_DEFAULT_ENV" != "build" ]; then
    echo "Failed to load conda environment named 'build'"
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

LOGFILE="${COMMIT:?Please set a COMMIT env variable}.output"

echo "START Building for commit $COMMIT"
git checkout $COMMIT
git submodule update --init
CMAKE_PREFIX_PATH=${CONDA_PREFIX:-"$(dirname $(which conda))/../"}
# Disable MKLDNN since it weirdly breaks builds
# python setup.py bdist_wheel
USE_MKLDNN=0 USE_CUDA=1 python setup.py bdist_wheel | tee "$LOGFILE"

if [ -d "dist" -a "$?" -eq 0 ]; then
    cp --update -t "$BUILD_DIR" dist/*
    cp -t "$BUILD_DIR" "$LOGFILE"
    echo "DONE build for commit $COMMIT"
else
    ERROR_FILE_OUTPUT="$BUILD_DIR/${LOGFILE/%.output/.failed_output}"
    cp "$LOGFILE" "$ERROR_FILE_OUTPUT"
    echo "ERROR There was an error building $COMMIT, see $ERROR_FILE_OUTPUT for configuration information"
    exit 1
fi