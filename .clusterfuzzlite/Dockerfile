FROM gcr.io/oss-fuzz-base/base-builder-python@sha256:cfcc123c40d4ecab777ac0f32f868177cb752950bf9f5d880f55e452adda5106
COPY . $SRC/buildnotify
WORKDIR $SRC/buildnotify
COPY .clusterfuzzlite/build.sh $SRC/
