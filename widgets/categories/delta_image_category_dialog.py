from tools.data import cached_data
from widgets.categories.delta_category_image_list import DeltaImageCategoryListItem
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GdkPixbuf, GObject


class DeltaImageCategoryDialog(Adw.Dialog):
    def __init__(self, category: str):
        def _on_item_toggled(item, file_path: str, is_checked: bool):
            file = Gio.File.new_for_path(file_path)
            if file is None:
                return
            if is_checked:
                cached_data.add_file_to_category(category=category, file=file)
            else:
                cached_data.remove_file_from_category(category, file=file)

        def apply_changes():
            self.close()
            self.emit("closed")

        super().__init__(
            title=category,
        )

        content_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
            margin_bottom=24,
            margin_end=24,
            margin_start=24,
            hexpand=True,
            vexpand=True
        )

        toolbar_view = Adw.ToolbarView()
        self.set_child(toolbar_view)

        header = Adw.HeaderBar()
        toolbar_view.add_top_bar(header)

        uploaded_files = cached_data.selected_files

        if uploaded_files.get_n_items() >= 1:
            scroll_window_widget = Gtk.ScrolledWindow(
                vexpand=True,
                hexpand=True,
                width_request=500,
                height_request=500
            )
            image_list_widget = Gtk.ListBox()
            image_list_widget.add_css_class("boxed-list")

            files_in_category = cached_data.get_files_from_category(category=category) or []
            files_in_category_paths = {
                f.get_path() for f in files_in_category if f.get_path()
            }

            for image_content in uploaded_files:
                path = image_content.get_path()
                if not path:
                    continue
                enabled = path in files_in_category_paths
                item_element = DeltaImageCategoryListItem(
                    file_path=path,
                    checked=enabled
                )
                item_element.connect("toggled-checkbox", _on_item_toggled)
                image_list_widget.append(item_element)

            scroll_window_widget.set_child(image_list_widget)
            content_box.append(scroll_window_widget)
        else:
            dialog = Gtk.Label(label="Please upload images first")
            content_box.append(dialog)

        save_button = Gtk.Button(label="Close")
        save_button.connect("clicked", lambda b: apply_changes())
        content_box.append(save_button)
        toolbar_view.set_content(content_box)
