from tools.data import cached_data
from widgets.image_list_item_widget import ImageListItemWidget
from widgets.categories.delta_image_category_dialog import DeltaImageCategoryDialog
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GdkPixbuf, GObject


class CategoryDialog(Adw.Dialog):
    __gsignals__ = {
        "category-deleted": (GObject.SignalFlags.RUN_FIRST, None, ())
    }
    def __init__(self, category: str):
        
        super().__init__(
            title=category,
        )

        def DeltaImages():
            def close_dialg():
                self.close()
            dialog = DeltaImageCategoryDialog(
                category=category
            )
            dialog.connect("closed", lambda b:close_dialg())
            dialog.present(self)
        def DeleteCategory():
            cached_data.delta_category(
                category=category,
                status_change="remove"
            )
            self.emit("category-deleted")
            self.close()
            

        toolbar_view = Adw.ToolbarView()
        self.set_child(toolbar_view)
        

        header = Adw.HeaderBar()
        toolbar_view.add_top_bar(header)
        
        content_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
            margin_bottom=24,
            margin_end=24,
            margin_start=24,
            # margin_top=24,
        )
        
        button_boxes = Gtk.Box(
            hexpand=True,
            spacing=10,
            orientation=Gtk.Orientation.VERTICAL
        )
    # add image button
        add_images_button = Gtk.Button(
            label="Add Images",
            hexpand=True
            )
        add_images_button.add_css_class("suggested-action")
        add_images_button.connect("clicked", lambda b:DeltaImages())
        # add_images_button.connect("clicked", lambda b:initial_image_file_picker(win))
    # delete category
        delete_category_button = Gtk.Button(
            label="Delete Category",
            hexpand=True
            )
        delete_category_button.add_css_class("destructive-action")
        delete_category_button.connect("clicked", lambda b:DeleteCategory())

        button_boxes.append(add_images_button)
        button_boxes.append(delete_category_button)

        files_in_category = cached_data.get_files_from_category(category)
        if files_in_category != None:
            print(files_in_category)
            scroll_window_widget = Gtk.ScrolledWindow(
                vexpand=True,
                hexpand=True,
                width_request=500,
                height_request=500
            )
            image_list_widget = Gtk.ListBox()
            image_list_widget.add_css_class("boxed-list")

            for image_content in files_in_category:
                item_element = ImageListItemWidget(file_path=image_content.get_path())
                image_list_widget.append(item_element)

            scroll_window_widget.set_child(image_list_widget)

            # file_stack_view.append(scroll_window_widget)
            content_box.append(scroll_window_widget)
        else:
            dialog = Gtk.Label(label="No images in this category yet!")
            content_box.append(dialog)
        content_box.append(button_boxes)

            
        toolbar_view.set_content(content_box)