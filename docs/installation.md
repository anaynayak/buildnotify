# Installation instructions

## Ubuntu installation (Utopic Unicorn 14.10 and beyond)

```commandline
sudo apt-get install buildnotify
```

Thanks to Daniel Lintott for getting BuildNotify integrated into the main debian archive. 

## Ubuntu installation (pre-14.10 Utopic Unicorn)
* Run the following commands in a terminal and then launch it from Menu > Internet > BuildNotify

```commandline
sudo add-apt-repository ppa:anay/ppa
sudo apt-get update
sudo apt-get install python-buildnotify
```

The PPA is currently setup at [https://launchpad.net/~anay/+archive/ppa](https://launchpad.net/~anay/+archive/ppa)

## Alternate/Manual installation

* Install missing dependencies from setup.sh
* pip install buildnotify

Once you have installed the application, [you can configure it to monitor CI servers](usage.md)