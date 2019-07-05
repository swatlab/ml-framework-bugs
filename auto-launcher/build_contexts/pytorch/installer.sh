#!/usr/bin/env bash

git checkout $1
git submodule update
CMAKE_PREFIX_PATH=${CONDA_PREFIX:-"$(dirname $(which conda))/../"}
# Disable MKLDNN since it weirdly breaks builds
USE_MKLDNN=0
# python setup.py bdist_wheel
echo 'python setup.py bdist_wheel'