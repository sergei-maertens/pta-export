#!/bin/bash

#
# Compile the dependencies for production, CI and development.
#
# Usage, in the root of the project:
#
#     ./bin/compile_dependencies.sh
#
# Any extra flags/arguments passed to this wrapper script are passed down to uv pip compile.
# E.g. to update a package:
#
#     ./bin/compile_dependencies.sh --upgrade-package django

set -ex

toplevel=$(git rev-parse --show-toplevel)

cd $toplevel

export UV_CUSTOM_COMPILE_COMMAND="./bin/compile_dependencies.sh"

# Base (& prod) deps
uv pip compile \
    --output-file requirements/base.txt \
    "$@" \
    requirements/base.in

# Dependencies for testing
uv pip compile \
    --output-file requirements/ci.txt \
    "$@" \
    requirements/base.txt \
    requirements/test-tools.in

# Dev depedencies - exact same set as CI + some extra tooling
uv pip compile \
    --output-file requirements/dev.txt \
    "$@" \
    requirements/ci.txt \
    requirements/dev.in
