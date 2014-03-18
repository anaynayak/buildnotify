
Local setup:

Virtualbox + Ubuntu Precise

Dependencies for running application and build script:

```
sudo apt-get update
sudo apt-get install python-qt4 qt4-dev-tools python-tz python-dateutil pyqt4-dev-tools python-support
sudo pip install paver
```

Complete list of available paver commands can be viewed by running @paver 

### Packaging


Dependencies for creating a deb package

```
sudo pip install stdeb
sudo apt-get install debhelper dput

```



```
cp NEW_ICON /usr/share/icons/hicolor/icon-success.svg
sudo gtk-update-icon-cache /usr/share/icons/hicolor
```

