# The Sims 4 Mod Manager

A lightweight, blazing-fast mod manager for The Sims 4. Built specifically to handle massive custom content libraries without lagging, crashing, or locking up your computer.

---

## ✨ Features
* **High Capacity Engine:** Optimized with background threading and page-by-page rendering. Easily handles collections up to 18,000+ mods instantly.
* **Smart Detection:** Automatically checks standard Windows, macOS, and OneDrive paths to locate your Sims 4 Mods directory out of the box.
* **Bulk Import:** Seamlessly import individual `.package`/`.ts4script` files or extract compressed `.zip` mods directly into your game folders.
* **Instant Live Filtering:** Search through thousands of files in real-time as you type, without triggering heavy drive re-scans.

---

## 🚀 How to Install & Run (For Regular Users)

You do **not** need to install Python, download the source code, or run any setup scripts to use this manager!

1. Look at the right-hand sidebar of this GitHub page and click on the latest **Release**.
2. Under the **Assets** section of that release, download the `sims_4_mod_manager.zip` file.
3. Right-click the downloaded ZIP file on your computer and select **Extract All**.
4. Open the extracted folder and double-click the application file to launch the manager!

---

## 🛡️ Note on Windows SmartScreen Warnings

Because this application is open-source and not signed with an expensive Microsoft commercial developer certificate, Windows SmartScreen will likely show a blue popup saying *"Windows protected your PC"* when you first run it.

**To bypass this and open the app:**
1. Click the small **"More Info"** link on the blue window.
2. Click the **"Run Anyway"** button that appears at the bottom.

*Note: If a local antivirus flags the file, this is a false positive caused by the PyInstaller compiler wrapping the script. The entire source code is completely transparent and viewable right here on this page for your peace of mind!*

---

## 🛠️ Development & Building From Source (For Programmers)

If you want to modify the source code, contribute features, or compile the executable file yourself on your local machine, use the setup steps below.

### Prerequisites
* Python 3.10 or higher
* Pip (Python package installer)

### 1. Environment Setup
Clone this repository to your local machine, open your terminal/command prompt inside the project folder, and install the layout dependencies:
bash
pip install customtkinter pyinstaller

----

### 2. Running the Raw Script
To run and test the live application directly from the source code without compiling:

bash
python app.py

## 3. Compiling into a Standalone Executable

If you modify the Python file and need to re-generate the executable file:

On Windows: Double-click or run the included build.bat script.

On macOS: Open terminal, grant execution permissions (chmod +x build.sh), and run ./build.sh.

The freshly compiled, standalone application will be generated inside the newly created dist/ folder.

----


'''