Local setup:

* Use Vagrantfile to launch a local VM
* Alternatively, use dependencies specified in setup.sh to setup a local machine


### Running tests

```
docker run -it --volume=/Absolute/Path/To/buildnotify:/buildnotify --workdir="/buildnotify" --memory=4g --memory-swap=4g --entrypoint=/bin/bash ubuntu:16.04
docker run -it --volume=/Users/Anay/Project/buildnotify:/buildnotify --workdir="/buildnotify" --memory=4g --memory-swap=4g --entrypoint=/bin/bash ubuntu:16.04

Run steps from .circleci/config.yml
```
apt-get install python-dev build-essential libffi-dev libssl-dev
pylint -f parseable buildnotifylib/ --disable=missing-docstring,too-many-instance-attributes,too-few-public-methods,too-many-arguments,too-many-public-methods >report.txt
```

Complete list of available paver commands can be viewed by running @paver 

### Packaging


Dependencies for creating a pip/deb package

```
sudo pip install paver
sudo pip install stdeb
sudo pip install twine
sudo pip install keyrings.alt
sudo apt-get install debhelper dput

```