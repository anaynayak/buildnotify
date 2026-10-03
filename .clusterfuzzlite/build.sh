#!/bin/bash -eu
# The fuzzed modules are in buildnotifylib.core, which needs only defusedxml, not Qt.
pip3 install --no-deps .
pip3 install defusedxml

for fuzzer in $(find fuzz -name 'fuzz_*.py'); do
  compile_python_fuzzer "$fuzzer"
done
