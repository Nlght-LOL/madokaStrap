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
> Linux support requires Wine and the required graphics libraries. The launcher automatically manages an isolated Wine prefix for Cartii and its related tools.

---

> [!WARNING]
>
> macOS support is currently limited and may not work correctly in all situations.

---

## ⭐ Features

* FastFlags support
* `cc://` URI support
* Automatic `cc://` protocol registration on Linux
* Linux support through Wine
* Isolated Wine prefix
* GE-Proton support through `umu-run`
* Automatic DXVK detection
* Automatic DXVK installation
* Automatic DXVK updates
* DXVK DLL configuration
* NVIDIA GPU support
* Intel GPU support
* AMD GPU support
* Madoka Studio launcher
* Cartii bootstrapper launcher
* WinRAR installation inside the Wine prefix
* 2017 client support
* 2018 client support
* 2020 client support
* 2021 client support
* Automatic PlaceLauncher URL generation
* Join ticket handling
* URI launch diagnostics
* Wine launch logging

---

# 📋 Requirements

## 🐍 Python

Cartii Launcher requires:

* Python 3.9 or newer
* `pip`

Check your installation:

```bash
python3 --version
pip3 --version
```

If Python is not installed on Debian-based distributions:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

---

## 📦 Python Dependencies

The launcher requires:

* `colorama`

Install it with:

```bash
pip3 install colorama
```

If you are using a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install colorama
```

You can also install all Python dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

A minimal `requirements.txt` is:

```text
colorama
```

---

# 🐧 Linux Requirements

Linux users need the following components:

* Wine
* 32-bit Wine libraries
* Mesa/OpenGL
* Vulkan
* `umu-run`
* GE-Proton
* DXVK
* `curl` or equivalent download tools
* `tar`
* `unzip`

The exact packages depend on your Linux distribution.

---

# 🍷 Wine

Wine is required for running Windows clients and applications.

Check whether Wine is installed:

```bash
wine --version
```

On Debian/Forky or Debian-based systems:

```bash
sudo apt update
sudo apt install wine wine64 wine32
```

If your distribution does not provide `wine32` directly, make sure the `i386` architecture is enabled:

```bash
sudo dpkg --add-architecture i386
sudo apt update
```

Then install the 32-bit Wine components:

```bash
sudo apt install wine32 wine64
```

Verify:

```bash
wine --version
wine64 --version
```

---

# 🖥️ OpenGL / Mesa

Cartii clients may require working OpenGL acceleration.

For Intel, AMD and Mesa-based graphics:

```bash
sudo apt install \
    libgl1-mesa-dri \
    libglx-mesa0 \
    mesa-utils \
    mesa-vulkan-drivers
```

For 32-bit applications, also install the i386 versions:

```bash
sudo apt install \
    libgl1-mesa-dri:i386 \
    libglx-mesa0:i386 \
    mesa-vulkan-drivers:i386
```

Verify OpenGL:

```bash
glxinfo -B
```

A working installation should report something similar to:

```text
direct rendering: Yes
Accelerated: yes
```

You should also see your actual GPU under:

```text
OpenGL vendor string
OpenGL renderer string
```

For example:

```text
OpenGL vendor string: Intel
OpenGL renderer string: Mesa Intel(R) Graphics
```

---

# 🎮 Vulkan

Vulkan is required by DXVK and may be used by GE-Proton.

Install the Vulkan drivers:

```bash
sudo apt install mesa-vulkan-drivers
```

For 32-bit Windows applications:

```bash
sudo apt install mesa-vulkan-drivers:i386
```

Install Vulkan utilities:

```bash
sudo apt install vulkan-tools
```

Test Vulkan:

```bash
vulkaninfo --summary
```

If Vulkan is working, the command should display information about your GPU and Vulkan implementation.

---

# 🧩 32-bit Graphics Libraries

Even on a 64-bit Linux installation, Windows applications may require 32-bit graphics libraries.

Enable the i386 architecture:

```bash
sudo dpkg --add-architecture i386
```

Then:

```bash
sudo apt update
```

Install the required libraries:

```bash
sudo apt install \
    libgl1-mesa-dri:i386 \
    libglx-mesa0:i386 \
    mesa-vulkan-drivers:i386 \
    libvulkan1:i386 \
    libdrm2:i386 \
    libgbm1:i386
```

This is particularly important when Wine reports graphics or DRI-related errors.

---

# 🔧 Mesa DRI Drivers

The Mesa DRI directory should normally contain graphics drivers such as:

```text
/usr/lib/x86_64-linux-gnu/dri/
```

For example, Intel systems may contain:

```text
iris_dri.so
```

Check:

```bash
find /usr -name 'iris_dri.so' 2>/dev/null
```

You can also check the directory:

```bash
ls -lah /usr/lib/x86_64-linux-gnu/dri/
```

If `iris_dri.so` exists there, Mesa's Intel Iris driver is installed.

---

# ⚠️ Fixing `iris: driver missing`

If you see:

```text
iris: driver missing
glx: failed to create dri3 screen
failed to load driver: iris
```

install or reinstall the Mesa packages:

```bash
sudo apt update

sudo apt install --reinstall \
    mesa-vulkan-drivers \
    mesa-vulkan-drivers:i386 \
    mesa-utils \
    libgl1-mesa-dri \
    libgl1-mesa-dri:i386 \
    libglx-mesa0 \
    libglx-mesa0:i386
```

Then verify:

```bash
glxinfo -B
```

Make sure it reports:

```text
direct rendering: Yes
Accelerated: yes
```

---

# 🚀 umu-run

GE-Proton is launched through `umu-run`.

Cartii Launcher searches for:

```text
umu-run
```

and also checks common locations such as:

```text
~/.local/bin/umu-run
/usr/bin/umu-run
/usr/local/bin/umu-run
```

Verify:

```bash
which umu-run
```

or:

```bash
~/.local/bin/umu-run --help
```

The launcher requires `umu-run` to be available before GE-Proton can be used.

---

# 🎮 GE-Proton

The launcher automatically downloads and manages GE-Proton.

The installed runtime is stored under the Cartii Launcher data directory.

The launcher automatically:

* Checks the latest GE-Proton release
* Downloads GE-Proton
* Extracts GE-Proton
* Validates the installation
* Selects GE-Proton as the active runtime
* Uses `PROTONPATH` when launching clients

The runtime environment uses:

```text
WINEPREFIX
PROTONPATH
GAMEID
STORE
UMU_LOG
```

The launcher also enables:

```text
PROTON_USE_WINED3D=1
```

for the current Cartii client launch configuration.

---

# 🎨 DXVK

DXVK provides Direct3D-to-Vulkan translation for Windows applications.

The launcher automatically handles DXVK during Linux setup.

It can:

* Detect DXVK
* Download DXVK
* Install DXVK
* Update DXVK
* Configure DLL overrides

The configured libraries include:

```text
d3d8
d3d9
d3d10core
d3d11
dxgi
```

---

# 🧪 Verify the Graphics Stack

Before troubleshooting Cartii, verify the Linux graphics stack.

### OpenGL

```bash
glxinfo -B
```

Expected:

```text
direct rendering: Yes
Accelerated: yes
```

### Vulkan

```bash
vulkaninfo --summary
```

### Wine

```bash
wine --version
```

### umu-run

```bash
which umu-run
```

### GPU driver

For Intel:

```bash
find /usr/lib/x86_64-linux-gnu/dri -name 'iris_dri.so'
```

For AMD:

```bash
find /usr/lib/x86_64-linux-gnu/dri -name 'radeonsi_dri.so'
```

---

# 📥 Installation

Clone the repository:

```bash
git clone https://github.com/Nlght-LOL/madokaStrap.git
```

Enter the directory:

```bash
cd madokaStrap
```

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

If `requirements.txt` does not exist:

```bash
pip install colorama
```

---

# ▶️ Running

Start the launcher with:

```bash
python3 launcher.py
```

If using the virtual environment:

```bash
source venv/bin/activate
python launcher.py
```

The main menu provides:

* Launch Studio
* Set FastFlags
* Launch `cartiiLauncher.exe`
* Setup Linux Integration
* Install WinRAR in WINEPREFIX
* Exit

Linux-specific options are only displayed when running on Linux.

---

# 🐧 Linux Setup

Selecting **Setup Linux Integration** automatically prepares the environment.

The setup performs:

* Wine detection
* Wine prefix preparation
* DXVK verification
* DXVK installation or update
* DXVK configuration
* Desktop integration
* `cc://` protocol registration

---

# 🍷 Isolated Wine Prefix

Cartii uses an isolated Wine prefix.

The prefix is located at:

```text
~/.local/share/wineprefixes/madoka
```

This prevents Cartii's Windows components from interfering with the user's normal Wine environment.

The launcher can automatically create and configure this prefix.

---

# 🔗 cc:// Support

Cartii Launcher supports launching games through `cc://` URIs.

The launcher can read:

* Place ID
* Join ticket
* Client year
* PlaceLauncher URL
* Launch mode
* Launch time
* User ID
* Universe ID

It converts the received information into the launch arguments required by the Cartii client.

URIs can also be launched manually:

```bash
python3 launcher.py --uri "cc://..."
```

---

# 🖥️ Desktop Integration

On Linux, the launcher registers itself as the handler for:

```text
x-scheme-handler/cc
```

This allows supported `cc://` links to automatically launch Cartii.

The desktop entry is created at:

```text
~/.local/share/applications/cartii-launcher.desktop
```

An uninstall entry is also created for removing the Linux integration.

---

# 🚩 FastFlags

The launcher includes a built-in FastFlags manager.

It allows you to:

* Add FastFlags
* Remove FastFlags
* Clear all FastFlags
* Apply FastFlags
* Import FastFlags from JSON
* Automatically detect value types

FastFlags are stored in:

```text
fastFlags.json
```

Supported value types include:

* Boolean
* Integer
* Floating-point
* String

FastFlags can be automatically applied to detected Cartii clients.

---

# 🎨 Madoka Studio

The launcher includes support for launching Madoka Studio.

On Linux, Madoka Studio is executed through Wine using the isolated Wine prefix.

---

# 📦 Cartii Bootstrapper

The launcher can start:

```text
cartiiLauncher.exe
```

directly.

On Linux, the bootstrapper is executed using the configured Wine/GE-Proton runtime.

The client arguments are passed dynamically to the runtime, allowing different client years and launch parameters to be used without hardcoding a specific year.

---

# 🗜️ WinRAR

The launcher can download and install WinRAR inside the isolated Wine prefix.

This allows WinRAR to remain separated from the user's normal Wine environment.

---

# 📋 Launch Diagnostics

When receiving a `cc://` URI, the launcher displays information about the game join.

It shows:

* Place ID
* Whether a ticket was received
* Whether a PlaceLauncher URL was received
* The selected client year
* The final launch arguments

This makes it easier to diagnose failed game launches.

---

# 📝 Wine Logging

Wine launch output is stored in:

```text
~/.local/share/wineprefixes/madoka/wine_launch.log
```

The log contains:

* Launcher version
* Received URI
* Client year
* Launch arguments
* Wine output

Join tickets are hidden when written to the diagnostic log.

---

# 📁 File Locations

| File / Directory                                                | Purpose                 |
| --------------------------------------------------------------- | ----------------------- |
| `~/.local/share/wineprefixes/madoka`                            | Isolated Wine prefix    |
| `~/.local/share/wineprefixes/madoka/.dxvk-version`              | Installed DXVK version  |
| `~/.local/share/wineprefixes/madoka/wine_launch.log`            | Wine launch log         |
| `fastFlags.json`                                                | FastFlags configuration |
| `~/.local/share/applications/cartii-launcher.desktop`           | Linux desktop entry     |
| `~/.local/share/applications/uninstall-cartii-launcher.desktop` | Linux uninstall entry   |

---

# 🛠️ Troubleshooting

## `wine: command not found`

Install Wine:

```bash
sudo apt update
sudo apt install wine wine64 wine32
```

---

## `umu-run was not found`

Check:

```bash
which umu-run
```

If it is installed in `~/.local/bin`:

```bash
ls -lah ~/.local/bin/umu-run
```

Make sure it is executable:

```bash
chmod +x ~/.local/bin/umu-run
```

---

## `iris: driver missing`

Install the Mesa DRI packages:

```bash
sudo apt install --reinstall \
    libgl1-mesa-dri \
    libgl1-mesa-dri:i386 \
    libglx-mesa0 \
    libglx-mesa0:i386 \
    mesa-vulkan-drivers \
    mesa-vulkan-drivers:i386
```

Then test:

```bash
glxinfo -B
```

You should have:

```text
direct rendering: Yes
Accelerated: yes
```

---

## `glx: failed to create dri3 screen`

First verify:

```bash
glxinfo -B
```

Then verify that the DRI directory exists:

```bash
ls /usr/lib/x86_64-linux-gnu/dri/
```

For Intel GPUs, check:

```bash
ls /usr/lib/x86_64-linux-gnu/dri/iris_dri.so
```

If necessary, reinstall Mesa:

```bash
sudo apt install --reinstall \
    libgl1-mesa-dri \
    libglx-mesa0 \
    mesa-vulkan-drivers
```

---

## OpenGL works but Cartii has no 3D rendering

Check:

```bash
glxinfo -B
```

and:

```bash
vulkaninfo --summary
```

If OpenGL reports:

```text
direct rendering: Yes
Accelerated: yes
```

but GE-Proton still cannot initialize graphics, verify that the launcher is using the correct Mesa DRI path:

```text
/usr/lib/x86_64-linux-gnu/dri
```

The GE-Proton launch environment uses:

```text
LIBGL_DRIVERS_PATH=/usr/lib/x86_64-linux-gnu/dri
```

---

# 🔍 Manual GE-Proton Test

To test GE-Proton independently of the launcher, the same runtime environment can be used manually.

Example:

```bash
PROTON_USE_WINED3D=1 \
LIBGL_DRIVERS_PATH=/usr/lib/x86_64-linux-gnu/dri \
WINEPREFIX="$HOME/.local/share/madoka-player/wineprefix" \
PROTONPATH="$HOME/.local/share/madoka-player/ge-proton/GE-Proton11-5" \
GAMEID=madoka-player \
STORE=none \
UMU_LOG=1 \
"$HOME/.local/bin/umu-run" \
'C:\users\steamuser\AppData\Local\cartiirev\Client2020\CartiPlayerBeta.exe'
```

Additional client arguments can be appended normally.

For example:

```bash
PROTON_USE_WINED3D=1 \
LIBGL_DRIVERS_PATH=/usr/lib/x86_64-linux-gnu/dri \
WINEPREFIX="$HOME/.local/share/madoka-player/wineprefix" \
PROTONPATH="$HOME/.local/share/madoka-player/ge-proton/GE-Proton11-5" \
GAMEID=madoka-player \
STORE=none \
UMU_LOG=1 \
"$HOME/.local/bin/umu-run" \
'C:\users\steamuser\AppData\Local\cartiirev\Client2020\CartiPlayerBeta.exe' \
-a "..." \
-j "..." \
-t "..." \
-placeId "21856"
```

The launcher dynamically passes the arguments received from the bootstrapper instead of hardcoding them.

---

# 🧹 Resetting the Wine Environment

If the Wine prefix becomes corrupted, the isolated prefix can be removed.

**Warning:** this removes applications and configuration stored inside the Cartii Wine prefix.

```bash
rm -rf ~/.local/share/wineprefixes/madoka
```

Afterward, run the Linux setup again:

```bash
python3 launcher.py
```

and select:

```text
Setup Linux Integration
```

---

# 🔄 Updating

Update the repository:

```bash
git pull
```

Update Python dependencies:

```bash
pip install -r requirements.txt --upgrade
```

GE-Proton and DXVK can be managed by the launcher when their respective setup/update functionality is used.

---

# 📜 License

Add the project's license information here.

---

> [!NOTE]
>
> Cartii Launcher is designed to simplify launching Cartii clients and managing the required Linux environment. Linux graphics support depends on the system's Wine, Mesa/Vulkan and GPU driver configuration.
