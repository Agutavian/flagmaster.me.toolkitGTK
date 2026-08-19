import os
import mimetypes
from concurrent.futures import ThreadPoolExecutor
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GdkPixbuf, GLib

# Global thread pool for off-main-thread I/O and thumbnail processing
_executor = ThreadPoolExecutor(max_workers=4)

# In-memory thumbnail cache: (path, width, height) -> GdkPixbuf.Pixbuf
_thumbnail_cache: dict[tuple[str, int, int], GdkPixbuf.Pixbuf] = {}


def is_valid_jpeg(path: str) -> bool:
    """Fast check for valid JPEG using magic bytes."""
    if not path or not os.path.isfile(path):
        return False
    try:
        with open(path, "rb") as file:
            header = file.read(3)
            return header == b"\xff\xd8\xff"
    except OSError:
        return False


def get_thumbnail_async(file_path: str, width: int, height: int, callback):
    """
    Asynchronously loads and scales a thumbnail pixbuf.
    Invokes `callback(pixbuf)` on the GLib main thread when ready.
    """
    key = (file_path, width, height)
    if key in _thumbnail_cache:
        callback(_thumbnail_cache[key])
        return

    def _worker():
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                file_path,
                width=width,
                height=height,
                preserve_aspect_ratio=True
            )
            pixbuf = GdkPixbuf.Pixbuf.apply_embedded_orientation(pixbuf)
            _thumbnail_cache[key] = pixbuf
            GLib.idle_add(callback, pixbuf)
        except Exception as e:
            GLib.idle_add(callback, None)

    _executor.submit(_worker)


def clear_listbox(listbox: Gtk.ListBox):
    """Removes all children from a Gtk.ListBox efficiently."""
    child = listbox.get_first_child()
    while child:
        next_child = child.get_next_sibling()
        listbox.remove(child)
        child = next_child


def clear_specific(listbox: Gtk.ListBox, widget):
    """Removes a specific child widget from a Gtk.ListBox."""
    child = listbox.get_first_child()
    while child:
        next_child = child.get_next_sibling()
        if child == widget:
            listbox.remove(child)
            break
        child = next_child
