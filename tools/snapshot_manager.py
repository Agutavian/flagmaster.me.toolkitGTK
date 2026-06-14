import gi
import os
import json
from tools.error_manager import warn_user_of_error
from tools.data import cached_data
from tools.misc import is_valid_jpeg
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, Gdk, GLib

### Format of snapshot (list of jsons)
# Snapshot to be used for internal data only
# [
# "/path/to/image": {
#   "catagories": "[]" todo when processing: check if the catagory exists. if it dosn't, add new one and append this file to it?
#   },
# ]


def import_snapshot(window: Adw.ApplicationWindow, on_completion):
    invalids: list[str] = []
    # Append images that don't already exist to selected_files

    # TBH this was made by chatgpt because I couldn't be bothered to code this headache myself
    def process_data(data: dict[str, list[str]]):
        def is_in_selected_files(path: str) -> bool:
            for file in cached_data.selected_files:
                file: Gio.File
                if file.get_path() == path:
                    return True
            return False

        invalids: dict[str, list[str]] = {}

        for category, image_paths in data.items():

            # Create category if it doesn't exist
            if category not in cached_data.categories_list:
                cached_data.categories_list[category] = []

            invalids[category] = []

            for path in image_paths:

                if not os.path.isfile(path):
                    invalids[category].append(path)
                    continue

                if not is_valid_jpeg(path):
                    invalids[category].append(path)
                    continue

                # Add image to selected_files if needed
                if not is_in_selected_files(path):
                    gio_file = Gio.File.new_for_path(path)
                    cached_data.selected_files.append(gio_file)

                # Add image to category if needed
                if path not in cached_data.categories_list[category]:
                    cached_data.categories_list[category].append(path)

            # Remove invalid entries from imported data
            for invalid_path in invalids[category]:
                data[category].remove(invalid_path)


    def process_snapshot(file: Gio.File):
        path = file.get_path()
        # first check if path is empty
        if path is None:
            warn_user_of_error(error_message="File path is empty")
            return
        # then try to open it
        try:
            with open(path, "r") as opened_file:
                # opened_file.read()
                # try to read it json-wise, see if it is correct json
                json_data: dict = json.load(opened_file) 
                process_data(json_data)
                if on_completion:
                    on_completion()
        except json.JSONDecodeError as error:
            print("error!")
            warn_user_of_error(error_message=f"{error}")
        # if theres a problem with opening the file 
        except OSError as error:
            print("error!")
            warn_user_of_error(error_message=f"{error}")
        # if theres a problem reading the file (not unicode)
        except UnicodeDecodeError as error:
            print("error!")
            warn_user_of_error(error_message=f"File is not valid: {error}")

    
    def on_file_recieved(dialog, result):
        try:
            file: Gio.File = dialog.open_finish(result)
            process_snapshot(file)
        except GLib.Error as error:
            print(f"Status: {error.message} (code: {error.code})")
            return

    import_dialog = Gtk.FileDialog()

    filter = Gtk.FileFilter()
    filter.set_name("JSON Config Files")
    filter.add_mime_type("application/json")

    filters = Gio.ListStore.new(Gtk.FileFilter)
    filters.append(filter)
    import_dialog.set_filters(filters)

    import_dialog.open(
        parent=window,
        callback=on_file_recieved
    )
        
def export_snapshot(window: Adw.ApplicationWindow):

    def on_save_chosen(dialog, result):
        try:
            file_result = dialog.save_finish(result)
            print(file_result.get_path())
            
            # if os.path.isfile(file_result.get_path()): # check if the file exists already
            file_write = open(file_result.get_path(), "w")
            json.dump(cached_data.categories_list, file_write, indent=2)
        except Exception as error:
            print(f"{error}")
            warn_user_of_error(f"{error}")

    export_dialog = Gtk.FileDialog(
        title="Save Config"
    )
    export_dialog.set_initial_name("flagmasterme_toolkit_config.json")


    export_dialog.save(
        window,
        None,
        on_save_chosen
    )
    
