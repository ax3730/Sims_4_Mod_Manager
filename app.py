import platform
import zipfile
import shutil
from pathlib import Path
from tkinter import filedialog
import customtkinter as ctk
import threading  # Added for background scanning

# --- Styling Variables ---
LILAC_COLOR = "#C3A6ED"
LILAC_HOVER = "#A388D4"

# Global list to track active checkbox widgets for filtering
stored_mod_widgets = []

# --- Folder Detection Logic ---
def get_mods_folder():
    current_os = platform.system()
    home = Path.home()
    
    if current_os == "Windows":
        standard_path = home / "Documents" / "Electronic Arts" / "The Sims 4" / "Mods"
        onedrive_path = home / "OneDrive" / "Documents" / "Electronic Arts" / "The Sims 4" / "Mods"
        return onedrive_path if onedrive_path.exists() else standard_path
    elif current_os == "Darwin":
        return home / "Documents" / "Sims4ModsTest"
    return None

# --- Core Mod Manager Logic ---
def toggle_mod(file_path, checkbox_variable):
    """Toggles a mod between active (.package/.ts4script) and .disabled."""
    if checkbox_variable.get() == 1:
        if file_path.suffix == ".disabled":
            new_path = file_path.with_suffix("") 
            file_path.rename(new_path)
            status_label.configure(text=f"Enabled: {new_path.name}", text_color="green")
    else:
        if file_path.suffix in [".package", ".ts4script"]:
            new_path = file_path.with_name(file_path.name + ".disabled")
            file_path.rename(new_path)
            status_label.configure(text=f"Disabled: {file_path.name}", text_color="orange")
            
    load_mods()

def extract_zip_mod():
    """Unzips the selected file into the mods folder."""
    mods_directory = get_mods_folder()
    if not mods_directory or not mods_directory.exists():
        status_label.configure(text="Error: Mods folder not found.", text_color="red")
        return

    zip_to_extract = filedialog.askopenfilename(
        title="Select a downloaded Mod Zip File",
        filetypes=[("Zip Files", "*.zip")]
    )
    
    if not zip_to_extract:
        return
        
    zip_path = Path(zip_to_extract)
    destination_folder = mods_directory / zip_path.stem
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(destination_folder)
            
        status_label.configure(text=f"Successfully imported ZIP: {zip_path.name}", text_color=LILAC_COLOR)
        search_entry.delete(0, "end")
        load_mods()
        
    except Exception as e:
        status_label.configure(text=f"Error extracting zip: {str(e)}", text_color="red")

def import_single_files():
    """Copies individual .package or .ts4script files."""
    mods_directory = get_mods_folder()
    if not mods_directory or not mods_directory.exists():
        status_label.configure(text="Error: Mods folder not found.", text_color="red")
        return

    files_to_import = filedialog.askopenfilenames(
        title="Select Mod Files",
        filetypes=[("Sims 4 Mods", "*.package *.ts4script")]
    )
    
    if not files_to_import:
        return
        
    success_count = 0
    errors = []

    for file in files_to_import:
        source_path = Path(file)
        destination_path = mods_directory / source_path.name
        
        try:
            shutil.copy2(source_path, destination_path)
            success_count += 1
        except Exception as e:
            errors.append(f"Error copying {source_path.name}: {str(e)}")
            
    if success_count > 0:
        status_label.configure(
            text=f"Imported {success_count} file(s) to Mods root.", 
            text_color=LILAC_COLOR
        )
        load_mods()
    
    if errors:
        print(f"Errors during import: {errors}")

def load_mods():
    """Scans the folder in a background thread and streams widgets dynamically to prevent crashing."""
    global stored_mod_widgets
    
    # Temporarily lock the refresh button so user can't spam double-clicks
    load_button.configure(state="disabled", text="Scanning...")
    status_label.configure(text="Searching mods folder...", text_color="white")
    
    # Clear old UI items safely
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    stored_mod_widgets = []

    def background_scan():
        mods_directory = get_mods_folder()
        found_files = []
        
        if mods_directory and mods_directory.exists():
            for file in mods_directory.rglob("*"):
                if file.is_file():
                    is_disabled = file.suffix == ".disabled"
                    if file.suffix in [".package", ".ts4script"] or is_disabled:
                        found_files.append(file)
                        
        # Hand the files back to the main thread to safely update the UI in batches
        app.after(0, lambda: stream_widgets_to_ui(found_files))

    # Fire off the thread
    threading.Thread(target=background_scan, daemon=True).start()

def stream_widgets_to_ui(files):
    """Loads checkboxes in small batches so Windows doesn't lock up or freeze."""
    global stored_mod_widgets
    mods_directory = get_mods_folder()
    
    if not files:
        status_label.configure(text="No mods found in folder.", text_color="orange")
        load_button.configure(state="normal", text="Refresh List")
        return

    status_label.configure(text=f"Loading {len(files)} mods...", text_color=LILAC_COLOR)
    
    current_index = 0
    batch_size = 30  # Number of mods to load per frame ticket

    def load_next_batch():
        nonlocal current_index
        end_index = min(current_index + batch_size, len(files))
        
        for i in range(current_index, end_index):
            file = files[i]
            is_disabled = file.suffix == ".disabled"
            display_name = file.stem if is_disabled else file.name
            
            if file.parent != mods_directory:
                display_name = f"[{file.parent.name}] -> {display_name}"
                
            chk_var = ctk.IntVar(value=0 if is_disabled else 1)
            
            chk = ctk.CTkCheckBox(
                scrollable_frame, 
                text=display_name, 
                variable=chk_var,
                fg_color=LILAC_COLOR, 
                hover_color=LILAC_HOVER,
                command=lambda f=file, v=chk_var: toggle_mod(f, v)
            )
            chk.pack(anchor="w", pady=5, padx=10)
            stored_mod_widgets.append({"widget": chk, "name": display_name})
            
        current_index = end_index
        
        if current_index < len(files):
            # Give the UI 10 milliseconds to breathe and process clicks, then load next batch
            app.after(10, load_next_batch)
        else:
            # Everything is officially loaded
            status_label.configure(text=f"Successfully synchronized {len(files)} mods.", text_color="green")
            load_button.configure(state="normal", text="Refresh List")
            filter_mods()

def filter_mods(event=None):
    """Filters the visible checkboxes based on the search term."""
    search_term = search_entry.get().lower()
    for item in stored_mod_widgets:
        if search_term in item["name"].lower():
            item["widget"].pack(anchor="w", pady=5, padx=10)
        else:
            item["widget"].pack_forget()

# --- UI Layout Setup ---
app = ctk.CTk()
app.title("Lycanery's Mod Manager")
app.geometry("700x700") 
ctk.set_appearance_mode("dark")

title_label = ctk.CTkLabel(app, text="Lycanery's Mod Manager", font=("Arial", 28, "bold"), text_color=LILAC_COLOR)
title_label.pack(pady=20)

search_entry = ctk.CTkEntry(app, width=600, placeholder_text="🔍 Search your mods...")
search_entry.pack(pady=10, padx=20)
search_entry.bind("<KeyRelease>", filter_mods)

status_label = ctk.CTkLabel(app, text="Click Refresh to begin.", font=("Arial", 12))
status_label.pack(pady=5)

button_frame = ctk.CTkFrame(app, fg_color="transparent")
button_frame.pack(pady=15)

load_button = ctk.CTkButton(
    button_frame, 
    text="Refresh List", 
    command=load_mods, 
    font=("Arial", 14),
    border_width=1,
    border_color=LILAC_COLOR,
    fg_color="transparent", 
    text_color=LILAC_COLOR,
    hover_color="#2B2B2B"
)
load_button.pack(side="left", padx=10)

import_file_button = ctk.CTkButton(
    button_frame, 
    text="Import Files (.package)", 
    command=import_single_files, 
    font=("Arial", 14),
    fg_color=LILAC_COLOR, 
    text_color="black", 
    hover_color=LILAC_HOVER
)
import_file_button.pack(side="left", padx=10)

import_zip_button = ctk.CTkButton(
    button_frame, 
    text="Import Mod (.zip)", 
    command=extract_zip_mod, 
    font=("Arial", 14),
    fg_color=LILAC_COLOR, 
    text_color="black",
    hover_color=LILAC_HOVER
)
import_zip_button.pack(side="left", padx=10)

scrollable_frame = ctk.CTkScrollableFrame(
    app, 
    width=600, 
    height=380,
    border_width=1,
    border_color="#333333"
)
scrollable_frame.pack(pady=10, padx=20)

app.after(100, load_mods)

app.mainloop()