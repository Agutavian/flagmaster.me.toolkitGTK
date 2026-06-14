import mimetypes
from tools.data import cached_data
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GdkPixbuf


def is_valid_jpeg(path: str):
    # print(f"IsValidJPEG ")
    # print(path)
    try:
        with open(path, "rb") as file:
            mime, _ = mimetypes.guess_file_type(path)
            if mime != ("image/jpeg" or "image/jpg"):
                print(f"{path} isn't valid jpeg")
                print(mimetypes.guess_file_type(path))
                return False
            else:
                # print("Is valid jpeg/jpg!")
                return True
    except OSError as error:
        print(f"IsValidJPEG Error: {error}")
        return False
    

        
def clear_listbox(listbox):
    child = listbox.get_first_child()
    while child:
        next_child = child.get_next_sibling()
        listbox.remove(child)
        child = next_child


def clear_specific(listbox, image_path):
    child = listbox.get_first_child()
    while child:
        next_child = child.get_next_sibling()
        if child == image_path:
            listbox.remove(child)
        child = next_child
