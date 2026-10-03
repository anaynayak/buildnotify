#!/bin/bash -eu
# The fuzzed modules are in buildnotifylib.core, which needs only defusedxml, not Qt.
# atheris ships in the base image. Hashes come from .clusterfuzzlite/requirements.txt (just fuzz-reqs).
pip3 install --require-hashes --no-deps -r .clusterfuzzlite/requirements.txt
pip3 install --no-deps .

for fuzzer in $(find fuzz -name 'fuzz_*.py'); do
  compile_python_fuzzer "$fuzzer"
done
