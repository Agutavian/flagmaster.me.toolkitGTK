import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gio, Gtk

class CachedData():
    def __init__(self):
        self.selected_files = Gio.ListStore.new(Gio.File)  # type: ignore # type: Gio.ListStore[Gio.File]
        # First string is category name, second is file_path
        self.categories_list: dict[str, list[str]] = {}
        self.active_snapshot: dict = {}

        # 
        self.new_images = {}
        """
        {"file_path": "remove"}
        remove = remove from category
        add = add from category 
        """
    def clear_all_images(self):
        self.selected_files = Gio.ListStore.new(Gio.File)
        for category in self.categories_list:
            self.categories_list[category] = []

    def add_file_to_category(self, category: str, file: Gio.File):
        path = file.get_path()
        if path == None:
            raise Exception(f"path does exist: {file}")   
        elif path in self.categories_list[category]:
            return
        else:
            self.categories_list[category].append(path)

    def remove_file_from_category(self, category: str, file: Gio.File):
        path = file.get_path()
        if path == None:
            raise Exception(f"path does exist: {file}")    
        self.categories_list[category].remove(path)

    def get_files_from_category(self, category: str) -> list[Gio.File]|None:
        # if self.categories_list[category]
        if category in self.categories_list:
            to_return: list[Gio.File] = []
            for element in self.categories_list[category]:
                file = Gio.File.new_for_path(element)
                to_return.append(file)
            if len(to_return) == 0:
                return None
            return to_return
        else:
            raise Exception(f"Category does not exist: {category}")
    def delta_category(self, category: str, status_change: str):
        """
        status_change:
            "remove" -> remove category
            "add" -> add category
        """
        match status_change:
            case "add": 
                if category in self.categories_list:
                    raise Exception(f"Category already exists: {category}")
                else:
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
        else:
            # each file is a gio.file
            for file in self.selected_files:
                file: Gio.File
                if self.active_snapshot.get(file.get_path()):
                    continue
                    # temp_dict: dict = self.active_snapshot.get(file_name, {})
                    # # if this retunrs true, it means that the file already exists in self.active_snapshot, therefore, go to the next iteration of the loop
                    # if temp_dict.get(file.get_path()) == file.get_path:
                    #     continue
                    # else:
                    #     pass
                    
                self.active_snapshot[file.get_path()] = {
                    "categories": []
                }
                
cached_data = CachedData()