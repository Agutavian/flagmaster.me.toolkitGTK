import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gio, Gtk

class CachedData():
    def __init__(self):
        self.selected_files = Gio.ListStore.new(Gio.File)
        self._selected_paths: set[str] = set()
        # First string is category name, second is list of file_paths
        self.categories_list: dict[str, list[str]] = {}
        self.active_snapshot: dict = {}
        self.new_images = {}

    def is_file_selected(self, path: str) -> bool:
        return path in self._selected_paths

    def add_selected_file(self, file: Gio.File) -> bool:
        path = file.get_path()
        if not path or path in self._selected_paths:
            return False
        self._selected_paths.add(path)
        self.selected_files.append(file)
        return True

    def clear_all_images(self):
        self.selected_files.remove_all()
        self._selected_paths.clear()
        for category in self.categories_list:
            self.categories_list[category] = []

    def add_file_to_category(self, category: str, file: Gio.File):
        path = file.get_path()
        if path is None:
            raise Exception(f"File path is invalid: {file}")
        if category not in self.categories_list:
            self.categories_list[category] = []
        if path not in self.categories_list[category]:
            self.categories_list[category].append(path)

    def remove_file_from_category(self, category: str, file: Gio.File):
        path = file.get_path()
        if path is None:
            raise Exception(f"File path is invalid: {file}")
        if category in self.categories_list and path in self.categories_list[category]:
            self.categories_list[category].remove(path)

    def get_files_from_category(self, category: str) -> list[Gio.File] | None:
        if category in self.categories_list:
            to_return = [
                Gio.File.new_for_path(path)
                for path in self.categories_list[category]
                if path
            ]
            return to_return if to_return else None
        else:
            raise Exception(f"Category does not exist: {category}")

    def delta_category(self, category: str, status_change: str):
        match status_change:
            case "add":
                if category in self.categories_list:
                    raise Exception(f"Category already exists: {category}")
                self.categories_list[category] = []

            case "remove":
                if category in self.categories_list:
                    self.categories_list.pop(category)
                else:
                    raise Exception(f"Category does not exist: {category}")

            case _:
                raise Exception(f"Incorrect status_change variable given: {status_change}")

    def update_snapshot_images(self):
        if self.selected_files.get_n_items() == 0:
            return
        for file in self.selected_files:
            file_path = file.get_path()
            if file_path and file_path not in self.active_snapshot:
                self.active_snapshot[file_path] = {
                    "categories": []
                }

cached_data = CachedData()
