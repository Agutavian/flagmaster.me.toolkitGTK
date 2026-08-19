import os
import json
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GLib

from tools.error_manager import warn_user_of_error
from tools.data import cached_data
from tools.misc import is_valid_jpeg


def import_snapshot(window: Adw.ApplicationWindow, on_completion):
    def process_data(data: dict[str, list[str]]):
        for category, image_paths in data.items():
            if category not in cached_data.categories_list:
                cached_data.categories_list[category] = []

            for path in image_paths:
                if not os.path.isfile(path) or not is_valid_jpeg(path):
                    continue

                gio_file = Gio.File.new_for_path(path)
                cached_data.add_selected_file(gio_file)

                if path not in cached_data.categories_list[category]:
                    cached_data.categories_list[category].append(path)

    def process_snapshot(file: Gio.File):
        path = file.get_path()
        if path is None:
            warn_user_of_error(error_message="File path is empty")
            return
        try:
            with open(path, "r", encoding="utf-8") as opened_file:
                json_data: dict = json.load(opened_file)
                process_data(json_data)
                if on_completion:
                    on_completion()
        except (json.JSONDecodeError, OSError, UnicodeDecodeError) as error:
            warn_user_of_error(error_message=f"Failed to load snapshot: {error}")

    def on_file_received(dialog, result):
        try:
            file: Gio.File = dialog.open_finish(result)
            process_snapshot(file)
        except GLib.Error as error:
            print(f"Status: {error.message} (code: {error.code})")
            return

    import_dialog = Gtk.FileDialog()

    filter_json = Gtk.FileFilter()
    filter_json.set_name("JSON Config Files")
    filter_json.add_mime_type("application/json")

    filters = Gio.ListStore.new(Gtk.FileFilter)
    filters.append(filter_json)
    import_dialog.set_filters(filters)

    import_dialog.open(
        parent=window,
        callback=on_file_received
    )


def export_snapshot(window: Adw.ApplicationWindow):
    def on_save_chosen(dialog, result):
        try:
            file_result = dialog.save_finish(result)
            save_path = file_result.get_path()
            if save_path:
                with open(save_path, "w", encoding="utf-8") as file_write:
                    json.dump(cached_data.categories_list, file_write, indent=2)
                warn_user_of_error("Snapshot exported successfully")
        except Exception as error:
            warn_user_of_error(f"Failed to export snapshot: {error}")

    export_dialog = Gtk.FileDialog(title="Save Config")
    export_dialog.set_initial_name("flagmasterme_toolkit_config.json")
    export_dialog.save(window, None, on_save_chosen)
