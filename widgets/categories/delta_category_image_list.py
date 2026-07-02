import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GdkPixbuf, GObject


class DeltaImageCategoryListItem(Adw.ActionRow):
    __gsignals__ = {
        "toggled-checkbox": (GObject.SignalFlags.RUN_FIRST, None, (str, bool))
    }
    def __init__(self, file_path, checked: bool = False):
        super().__init__(
            title=file_path.split("/")[-1],
            subtitle=file_path
        )

        self.file_path = file_path
        # self.file_name = file_name

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            file_path,
            width=64,
            height=64,
            preserve_aspect_ratio=True
            )
        pixbuf = GdkPixbuf.Pixbuf.apply_embedded_orientation(pixbuf) # type: ignore

        image = Gtk.Image.new_from_pixbuf(pixbuf)

        image.set_pixel_size(64)
        self.add_prefix(image)


        checkbox = Gtk.CheckButton(active=checked)
        checkbox.connect("toggled", self._on_checkbox_toggled)

        self.add_suffix(checkbox)

    def _on_checkbox_toggled(self, checkbox):
        self.emit("toggled-checkbox", self.file_path, checkbox.get_active())