from tools.data import cached_data
from widgets.categories.category_setting_dialog import CategoryDialog
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GdkPixbuf


class CreateCategoryDialog(Adw.Dialog):
    def _add_category(self, category_name: str):
        try:
            cached_data.delta_category(
            category= category_name,
            status_change="add")
            # print(cached_data.categories_list)
            self.on_create()
            self.close()
        except Exception as e:
            print(f"Failed to add category: {e}")
    def __init__(self, on_completion):
        super().__init__(
            title="Create a new Category",
        )
        self.on_create = on_completion
        container = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
            margin_bottom=12,
            margin_end=12,
            margin_start=12,
            margin_top=12
        )
        enter_dialog = Gtk.Entry(
            hexpand=True,
            placeholder_text="New Category Name"
        )

        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.set_hexpand(True)
        cancel_button.set_halign(Gtk.Align.FILL)
        cancel_button.connect("clicked", lambda b: self.close())

        save_button = Gtk.Button(label="Save")
        save_button.set_hexpand(True)
        save_button.set_halign(Gtk.Align.FILL)
        save_button.add_css_class("suggested-action")

        save_button.connect("clicked", lambda b: self._add_category(enter_dialog.get_text()))

        button_row = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=6
        )

        button_row.append(cancel_button)
        button_row.append(save_button)

        
        container.append(enter_dialog)
        container.append(button_row)

        
        self.set_child(container)
        