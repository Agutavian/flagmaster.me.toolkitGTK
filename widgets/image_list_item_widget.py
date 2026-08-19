import os
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GdkPixbuf
from tools.misc import get_thumbnail_async


class ImageListItemWidget(Adw.ActionRow):
    def __init__(self, file_path: str):
        filename = os.path.basename(file_path)
        super().__init__(
            title=filename,
            subtitle=file_path
        )

        self.file_path = file_path

        # Placeholder image while thumbnail loads asynchronously
        self.image_widget = Gtk.Image.new_from_icon_name("image-x-generic-symbolic")
        self.image_widget.set_pixel_size(64)
        self.add_prefix(self.image_widget)

        # Async load scaled thumbnail
        get_thumbnail_async(file_path, 64, 64, self._on_thumbnail_loaded)

    def _on_thumbnail_loaded(self, pixbuf):
        if pixbuf and self.image_widget:
            self.image_widget.set_from_pixbuf(pixbuf)
