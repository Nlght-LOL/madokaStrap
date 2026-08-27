
<h1 align="center">Cartii Launcher</h1>

<p align="center">

  <i>A custom launcher for Cartii, with FastFlags, cc:// support and Linux integration.</i>

</p>

<p align="center">

  <i>Linux support with Wine, DXVK and an isolated environment.</i>

</p>

<p align="center">

  <i>If you can, please support the project. Every bit counts!</i>

</p>

> [!NOTE]
>
> Linux support requires Wine. The launcher automatically manages an isolated Wine prefix for Cartii and its related tools.

---

> [!WARNING]
>
> macOS support is currently limited and may not work correctly in all situations.

---

## ⭐ Features

- FastFlags support
- `cc://` URI support
- Automatic `cc://` protocol registration on Linux
- Linux support through Wine
- Isolated Wine prefix
- Automatic DXVK detection
- Automatic DXVK installation
- Automatic DXVK updates
- DXVK DLL configuration
- NVIDIA GPU support
- Madoka Studio launcher
- Cartii bootstrapper launcher
- WinRAR installation inside the Wine prefix
- 2017 client support
- 2018 client support
- 2020 client support
- 2021 client support
- Automatic PlaceLauncher URL generation
- Join ticket handling
- URI launch diagnostics
- Wine launch logging

---

## 🐧 Linux Support

The launcher provides a dedicated Wine environment for running Cartii and other Windows applications on Linux.

The isolated Wine prefix is located at:

`~/.local/share/wineprefixes/madoka`

The Linux setup can automatically:

- Detect Wine
- Create the Wine prefix
- Check the installed DXVK version
- Download DXVK
- Install DXVK
- Update DXVK
- Configure DXVK DLL overrides
- Create the desktop entry
- Register the `cc://` protocol

---

## 🎮 DXVK

The launcher automatically checks for DXVK during Linux setup.

The installed DXVK version is stored in:

`~/.local/share/wineprefixes/madoka/.dxvk-version`

If a newer version is available, it can automatically download and install it.

The configured DXVK libraries include:

- `d3d8`
- `d3d9`
- `d3d10core`
- `d3d11`
- `dxgi`

---

## 🔗 cc:// Support

Cartii Launcher supports launching games through `cc://` URIs.

The launcher can read:

- Place ID
- Join ticket
- Client year
- PlaceLauncher URL
- Launch mode
- Launch time
- User ID
- Universe ID

It converts the received information into the launch arguments required by the Cartii client.

URIs can also be launched manually with:

`python3 launcher.py --uri "cc://..."`

---

## 🖥️ Desktop Integration

On Linux, the launcher registers itself as the handler for:

`x-scheme-handler/cc`

This allows supported `cc://` links to automatically launch Cartii.

The desktop entry is created at:

`~/.local/share/applications/cartii-launcher.desktop`

An uninstall entry is also created for removing the Linux integration.

---

## 🚩 FastFlags

The launcher includes a built-in FastFlags manager.

It allows you to:

- Add FastFlags
- Remove FastFlags
- Clear all FastFlags
- Apply FastFlags
- Import FastFlags from JSON
- Automatically detect value types

FastFlags are stored in:

`fastFlags.json`

Supported value types include:

- Boolean
- Integer
- Floating-point
- String

FastFlags can be automatically applied to detected Cartii clients.

---

## 🎨 Madoka Studio

The launcher includes support for launching Madoka Studio.

On Linux, Madoka Studio is executed through Wine using the isolated Wine prefix.

---

## 📦 Cartii Bootstrapper

The launcher can start `cartiiLauncher.exe` directly.

On Linux, the bootstrapper is copied into the isolated Wine prefix before being executed.

---

## 🗜️ WinRAR

The launcher can download and install WinRAR inside the isolated Wine prefix.

This allows WinRAR to remain separated from the user's normal Wine environment.

---

## 📋 Launch Diagnostics

When receiving a `cc://` URI, the launcher displays information about the game join.

It shows:

- Place ID
- Whether a ticket was received
- Whether a PlaceLauncher URL was received
- The selected client year
- The final launch arguments

This makes it easier to diagnose failed game launches.

---

## 📝 Wine Logging

Wine launch output is stored in:

`~/.local/share/wineprefixes/madoka/wine_launch.log`

The log contains:

- Launcher version
- Received URI
- Client year
- Launch arguments
- Wine output

Join tickets are hidden when written to the diagnostic log.

---

## 📁 File Locations

- Wine prefix: `~/.local/share/wineprefixes/madoka`
- DXVK version: `~/.local/share/wineprefixes/madoka/.dxvk-version`
- Wine log: `~/.local/share/wineprefixes/madoka/wine_launch.log`
- FastFlags: `fastFlags.json`
- Desktop entry: `~/.local/share/applications/cartii-launcher.desktop`
- Uninstaller entry: `~/.local/share/applications/uninstall-cartii-launcher.desktop`

---

## 🚀 Usage

Start the launcher with:

`python3 launcher.py`

The main menu provides:

- Launch Studio
- Set FastFlags
- Launch `cartiiLauncher.exe`
- Setup Linux Integration
- Install WinRAR in WINEPREFIX
- Exit

Linux-specific options are only displayed when running on Linux.

---

## ⚙️ Linux Setup

Selecting **Setup Linux Integration** automatically prepares the environment.

The setup performs:

- Wine detection
- Wine prefix preparation
- DXVK verification
- DXVK installation or update
- DXVK configuration
- Desktop integration
- `cc://` protocol registration
> [!NOTE]
>
> Cartii Launcher is designed to simplify launching Cartii clients and managing the required Linux environment.