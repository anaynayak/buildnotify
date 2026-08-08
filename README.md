

# BuildNotify

BuildNotify is a cross-platform system tray application for monitoring build statuses on continuous integration (CI) servers. Designed as a modern equivalent to CCMenu/CCTray, it resides in your system tray and provides real-time notifications for project build changes, making it easy to keep track of your development pipelines.

## Features
- **Multi-Server Support**: Monitor projects across multiple CruiseControl and CCTray-compatible CI servers.
- **System Tray Integration**: Quick access to overall CI status and individual project dashboards from the system tray.
- **Smart Notifications**: Receive desktop alerts for broken, fixed, and still-failing builds.
- **Customizable UI**: Configure polling intervals, notification preferences, build sort order, and display prefixes via a built-in preferences dialog.
- **Cross-Platform**: Built with PyQt5, ensuring compatibility across Linux, Windows, and macOS environments.
- **Authentication Support**: Securely fetch build statuses from servers requiring credentials using the system keyring.

## Installation

### Ubuntu / Debian
**For Ubuntu 14.10 (Utopic Unicorn) and newer:**
```bash
sudo apt-get install buildnotify
```

**For older Ubuntu versions (via PPA):**
```bash
sudo add-apt-repository ppa:anay/ppa
sudo apt-get update
sudo apt-get install python-buildnotify
```

### PyPI
You can install the latest stable release directly via `pip`:
```bash
pip install buildnotify
```

### Prerequisites
Ensure the following system dependencies are installed before running manually:
```bash
sudo apt-get install python3-pyqt5 python3-tz python3-dateutil python3-keyring
```

## Usage

Once installed, launch the application:
```bash
python buildnotifyapplet.py
```
*(Or simply run `buildnotify` if installed via package managers.)*

### Configuration
1. Right-click the BuildNotify icon in your system tray.
2. Select **Preferences** to open the configuration dialog.
3. Under the **Servers** tab, add the URL of your CI server's CCTray feed (e.g., `http://ci-server:8080/cc.xml`).
4. Optionally configure authentication, project filters, and custom display prefixes for your projects.
5. Adjust **Notifications** and **Misc** settings to control polling intervals, build sorting, and alert triggers.

### Tray Menu
- **Left-Click**: Opens the full project list menu.
- **Project Items**: Click any project name to open its CI dashboard page in your default web browser.
- **Tooltips**: Hover over the tray icon to see the last check time. Right-click for options including **About** and **Exit**.

## Development

To set up a local development environment:

1. Clone the repository and create a virtual environment:
   ```bash
   git clone https://github.com/anaynayak/buildnotify.git
   cd buildnotify
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install development and test dependencies:
   ```bash
   pip install -r test-requirements.txt
   pip install -e .
   ```
3. Run the test suite:
   ```bash
   tox
   ```
4. Regenerate UI and icon resources (if modifying `.ui` or `.qrc` files):
   ```bash
   pip install paver
   paver mk_resources
   ```
5. Launch the app locally:
   ```bash
   python buildnotifyapplet.py
   ```

## Contributing
We welcome contributions! Please review the [Code of Conduct](CODE_OF_CONDUCT.md) and feel free to open issues or pull requests for bugs, features, or improvements.

## License
BuildNotify is open-source software. See the repository license file for details.
