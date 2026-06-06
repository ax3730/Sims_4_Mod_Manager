import platform
import zipfile
import shutil
from pathlib import Path
from tkinter import filedialog
import customtkinter as ctk
import threading

# --- Styling Variables ---
LILAC_COLOR = "#C3A6ED"
LILAC_HOVER = "#A388D4"

# --- High-Capacity Global Tracking ---
all_files = []          # Master list of all Path objects found on disk
filtered_files = []     # List of Path objects matching the current search
current_page = 0        # Track what page the user is currently looking at
ITEMS_PER_PAGE = 50     # Max checkboxes to show on screen at once

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
    """Toggles a mod between active (.package/.ts4script) and .disabled without reloading the whole drive."""
    global all_files, filtered_files
    try:
        if checkbox_variable.get() == 1:
            if file_path.suffix == ".disabled":
                new_path = file_path.with_suffix("") 
                file_path.rename(new_path)
                status_label.configure(text=f"Enabled: {new_path.name}", text_color="green")
                # Update our memory lists inline so we don't break if toggled again immediately
                if file_path in all_files: all_files[all_files.index(file_path)] = new_path
                if file_path in filtered_files: filtered_files[filtered_files.index(file_path)] = new_path
        else:
            if file_path.suffix in [".package", ".ts4script"]:
                new_path = file_path.with_name(file_path.name + ".disabled")
                file_path.rename(new_path)
                status_label.configure(text=f"Disabled: {file_path.name}", text_color="orange")
                # Update our memory lists inline
                if file_path in all_files: all_files[all_files.index(file_path)] = new_path
                if file_path in filtered_files: filtered_files[filtered_files.index(file_path)] = new_path
    except Exception as e:
        status_label.configure(text=f"Error toggling mod: {str(e)}", text_color="red")

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

# --- Engine & Pagination Optimization ---
def load_mods():
    """Quickly indexes files in a background thread without loading heavy graphics."""
    global all_files, filtered_files, current_page
    
    load_button.configure(state="disabled", text="Scanning...")
    status_label.configure(text="Deep scanning mods folder...", text_color="white")
    
    def background_scan():
        global all_files, filtered_files, current_page
        mods_directory = get_mods_folder()
        found = []
        
        if mods_directory and mods_directory.exists():
            for file in mods_directory.rglob("*"):
                if file.is_file():
                    is_disabled = file.suffix == ".disabled"
                    if file.suffix in [".package", ".ts4script"] or is_disabled:
                        found.append(file)
                        
        all_files = found
        filtered_files = list(found)
        current_page = 0
        
        # Hand back over to the main UI thread to render page 1 instantly
        app.after(0, render_current_page)

    threading.Thread(target=background_scan, daemon=True).start()

def render_current_page():
    """Renders exactly 50 checkboxes for the active page page instantly."""
    global filtered_files, current_page, ITEMS_PER_PAGE
    mods_directory = get_mods_folder()
    
    # Destroy only the existing visible checkboxes
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
        
    total_items = len(filtered_files)
    
    if total_items == 0:
        status_label.configure(text="No matching mods found.", text_color="orange")
        page_label.configure(text="Page 0 of 0")
        prev_button.configure(state="disabled")
        next_button.configure(state="disabled")
        load_button.configure(state="normal", text="Refresh List")
        return

    # Calculate slices
    start_idx = current_page * ITEMS_PER_PAGE
    end_idx = min(start_idx + ITEMS_PER_PAGE, total_items)
    total_pages = max(1, (total_items - 1) // ITEMS_PER_PAGE + 1)
    
    # Generate checkboxes only for this slice
    for i in range(start_idx, end_idx):
        file = filtered_files[i]
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

    # Update navigation details
    page_label.configure(text=f"Page {current_page + 1} of {total_pages}")
    status_label.configure(text=f"Showing mods {start_idx + 1}-{end_idx} of {total_items} total", text_color="green")
    
    # Handle button locking states
    prev_button.configure(state="normal" if current_page > 0 else "disabled")
    next_button.configure(state="normal" if current_page < total_pages - 1 else "disabled")
    load_button.configure(state="normal", text="Refresh List")

def filter_mods(event=None):
    """Filters the master list in memory instantly, resetting pagination."""
    global all_files, filtered_files, current_page
    search_term = search_entry.get().lower()
    
    filtered_files = [f for f in all_files if search_term in f.name.lower() or search_term in f.parent.name.lower()]
    current_page = 0
    render_current_page()

def next_page():
    global current_page
    current_page += 1
    render_current_page()

def prev_page():
    global current_page
    current_page -= 1
    render_current_page()

# --- UI Layout Setup ---
app = ctk.CTk()
app.title("The Sims 4 Mod Manager")
app.geometry("700x750")  # Bumped height slightly to accommodate pagination row cleanly
ctk.set_appearance_mode("dark")

title_label = ctk.CTkLabel(app, text="The Sims 4 Mod Manager", font=("Arial", 28, "bold"), text_color=LILAC_COLOR)
title_label.pack(pady=20)

search_entry = ctk.CTkEntry(app, width=600, placeholder_text="🔍 Search your mods...")
search_entry.pack(pady=10, padx=20)
search_entry.bind("<KeyRelease>", filter_mods)

status_label = ctk.CTkLabel(app, text="Click Refresh to begin.", font=("Arial", 12))
status_label.pack(pady=5)

button_frame = ctk.CTkFrame(app, fg_color="transparent")
button_frame.pack(pady=10)

load_button = ctk.CTkButton(
    button_frame, text="Refresh List", command=load_mods, font=("Arial", 14),
    border_width=1, border_color=LILAC_COLOR, fg_color="transparent", text_color=LILAC_COLOR, hover_color="#2B2B2B"
)
load_button.pack(side="left", padx=10)

import_file_button = ctk.CTkButton(
    button_frame, text="Import Files (.package)", command=import_single_files, font=("Arial", 14),
    fg_color=LILAC_COLOR, text_color="black", hover_color=LILAC_HOVER
)
import_file_button.pack(side="left", padx=10)

import_zip_button = ctk.CTkButton(
    button_frame, text="Import Mod (.zip)", command=extract_zip_mod, font=("Arial", 14),
    fg_color=LILAC_COLOR, text_color="black", hover_color=LILAC_HOVER
)
import_zip_button.pack(side="left", padx=10)

scrollable_frame = ctk.CTkScrollableFrame(app, width=600, height=380, border_width=1, border_color="#333333")
scrollable_frame.pack(pady=10, padx=20)

# --- New Pagination Row Layout ---
pagination_frame = ctk.CTkFrame(app, fg_color="transparent")
pagination_frame.pack(pady=10)

prev_button = ctk.CTkButton(
    pagination_frame, text="◀ Previous", command=prev_page, width=100,
    fg_color="#333333", text_color="white", hover_color="#444444"
)
prev_button.pack(side="left", padx=20)

page_label = ctk.CTkLabel(pagination_frame, text="Page 1 of 1", font=("Arial", 14, "bold"))
page_label.pack(side="left", padx=20)

next_button = ctk.CTkButton(
    pagination_frame, text="Next ▶", command=next_page, width=100,
    fg_color="#333333", text_color="white", hover_color="#444444"
)
next_button.pack(side="left", padx=20)

app.after(100, load_mods)
app.mainloop()