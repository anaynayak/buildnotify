Local setup:

* Use Vagrantfile to launch a local VM
* Alternatively, use dependencies specified in setup.sh to setup a local machine


### Running tests

```
docker run -it --volume=/Absolute/Path/To/buildnotify:/buildnotify --workdir="/buildnotify" --memory=4g --memory-swap=4g --entrypoint=/bin/bash ubuntu:16.04
docker run -it --volume=/Users/Anay/Project/buildnotify:/buildnotify --workdir="/buildnotify" --memory=4g --memory-swap=4g --entrypoint=/bin/bash ubuntu:16.04

Run steps from bitbucket-pipelines.yml
```

Complete list of available paver commands can be viewed by running @paver 

### Packaging


Dependencies for creating a deb package

```
sudo pip install stdeb
sudo apt-get install debhelper dput

```