# FAQ

## What all do I need to run this on my machine?

The steps specified in the [Installation](installation.md) page should help you get started.

## Why is BuildNotify not a gnome-applet anymore?

Well, it turns out that there are a lot more desktop environments other than Gnome which are being actively used by users and writing an application which works on everything is a real pain. 

## Does this work on Windows or Mac?

Yes. The application has been rewritten in PyQt so that it can work across different environments. If it worked for your XYZ configuration, do let me know.

## Why PyQt? Why not Xyz?

PyQt saved me from the pain of writing environment specific code as currently there is no uniform way of providing system tray applications which would work on KDE/Gnome/MyOwnDesktopEnvironment. Besides, it works for Windows/Mac for free.