# 💜 Lycanery's Mod Manager

A beautiful, lightweight, lilac themed mod manager designed specifically for **The Sims 4** on Windows. Built with Python and CustomTkinter.

## ✨ Features
* **Auto Detection:** Automatically locates standard or OneDrive Sims 4 Mod directories on Windows.
* **Instant Sync:** Scans and displays active and disabled mods instantly on boot.
* **One Click Toggles:** Easily enable or disable `.package` and `.ts4script` mods without deleting them.
* **Smart Search:** Live filtering search bar to instantly find mods in massive folders.
* **Easy Import:** Dedicated single file copy utilities and automatic `.zip` archive extraction directly into organized subfolders.

---

## 🛠️ How to Build the Executable (Windows)

If you are pulling this repository onto a fresh Windows machine, follow these steps to generate the standalone `.exe` application:

### Prerequisites
1. Ensure **Python 3.10+** is installed from the Microsoft Store or Python.org.
2. *Important:* Make sure **"Add Python to PATH"** was checked during the Python installation.

### Automated Build Steps
1. Download or clone this repository to the Windows PC.
2. Double click the `build.bat` file.
3. The script will automatically install necessary dependencies (`customtkinter`, `pyinstaller`) and compile the application.
4. Once completed, open the newly created `dist` folder to find **`app.exe`**. Rename it to `Lycanery's Mod Manager.exe` and enjoy!