FROM gcr.io/oss-fuzz-base/base-builder-python@sha256:38a48455c198e5c2b5071426b11b764ecd52b60cd68c88e1a5685decc42f15d4
COPY . $SRC/buildnotify
WORKDIR $SRC/buildnotify
COPY .clusterfuzzlite/build.sh $SRC/
