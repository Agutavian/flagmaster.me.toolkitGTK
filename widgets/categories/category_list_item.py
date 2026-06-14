import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GdkPixbuf, GObject
from widgets.categories.category_setting_dialog import CategoryDialog


class CategoryListItem(Adw.ActionRow):
    __gsignals__ = {
        "category-deleted": (GObject.SignalFlags.RUN_FIRST, None, ())
    }
    def __init__(self, category_name: str, win: Adw.ApplicationWindow):
        super().__init__(
            title=category_name
        #     subtitle=file_path
        )


        def show_category_settings():
            dialog = CategoryDialog(
                category=category_name,
            )
            def remove_catalog():
                self.emit("category-deleted")
            dialog.connect("category-deleted", lambda b:remove_catalog())
            dialog.present(win)
            

        button = Gtk.Button(
            icon_name="preferences-system-symbolic",
            valign=Gtk.Align.CENTER
        )

        button.connect("clicked", lambda b:show_category_settings())
        
        self.add_suffix(button)
