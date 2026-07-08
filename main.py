import gi
import os
from tools.data import cached_data
from tools.snapshot_manager import import_snapshot, export_snapshot
from tools.error_manager import toast_overlay, warn_user_of_error
from tools.misc import clear_listbox
from tools.compiler import ImageCompilerClass
from tools.debug import debug
from widgets.categories.category_list_item import CategoryListItem
from widgets.image_list_item_widget import ImageListItemWidget
from widgets.categories.create_category_dialog import CreateCategoryDialog

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, Gdk, GLib

# TO 
# SELECTED_FILES: Gio.ListStore

# Global Vars
image_list_widget = Gtk.ListBox()
image_list_widget.add_css_class("boxed-list")
# image_list_widget.set_selection_mode(Gtk.SelectionMode.NONE)
adw_left_stack = Adw.ViewStack()
image_compiler_class = ImageCompilerClass()

# symbolic icon
# insert_image_symbolic = Gtk.Image.new_from_icon_name("insert-image")
added_category_widgets = []



def switch_file_box_state(state: str):
    """
    Three Possible States: upload_view (before the files have been uploaded) || file_view (after files have been added) || loading_view (after files have been uploaded, before they have been updated) || smart (figure it out smartly?)
    """

    if state == "smart":
        if cached_data.selected_files.get_n_items == 0:
            adw_left_stack.set_visible_child_name("upload_view")
        else:
            adw_left_stack.set_visible_child_name("file_view")
    else:
        print(adw_left_stack.get_visible_child_name())
        adw_left_stack.set_visible_child_name(state)
    


def on_image_files_selected(dialog, result):
    try:
        files = dialog.open_multiple_finish(result)

        def paths_equal(a, b):
            return a.get_path() == b.get_path()

        if cached_data.selected_files.get_n_items() > 0:
            for file in files:
                found, position = cached_data.selected_files.find_with_equal_func(file, paths_equal)
                if not found:
                    cached_data.selected_files.append(file)
        else:
            cached_data.selected_files = files
            cached_data.update_snapshot_images()
        switch_file_box_state("loading_view")
        after_loading()

    except Exception:
        print("Cancelled")



def after_loading():
    update_file_stack(image_list_widget)
    switch_file_box_state("file_view")
    return False

def initial_image_file_picker(window: Adw.ApplicationWindow):
    dialog = Gtk.FileDialog()
    filter = Gtk.FileFilter()
    filter.set_name("JPEG Images")
    filter.add_mime_type("image/jpeg")
    filter.add_mime_type("image/jpg")

    filters = Gio.ListStore.new(Gtk.FileFilter)
    filters.append(filter)
    dialog.set_filters(filters)

    dialog.open_multiple(window, None, on_image_files_selected)

def on_compile(
    path: str | None
):
    if path == None:
        warn_user_of_error("ERROR: Output path cannot be empty")
    elif not os.path.isdir(path):
        warn_user_of_error("ERROR: Output path is not a valid path")
    
def file_location_picker(text_field: Gtk.Entry, window: Adw.ApplicationWindow):

    # do stuff
    dialog = Gtk.FileDialog()

    

    def on_folder_selected(dialog, result):
        try:
            folder = dialog.select_folder_finish(result)
            if folder:
                text_field.set_text(folder.get_path())
        except:
            print("Cancled!")


    dialog.select_folder(
        parent=window,
        callback=on_folder_selected
    )


    # dialog.open_multiple(window, None, on_image_files_selected)

def update_file_stack(image_list_widget: Gtk.ListBox):
    print("updaing file_stack")
    # clear_listbox(image_list_widget)
    clear_listbox(listbox=image_list_widget)

    for file in cached_data.selected_files:
        image_list_widget.append(
            ImageListItemWidget(
                file_path= file.get_path()
            )
        )
    switch_file_box_state("smart")

def clear_images():
    clear_listbox(image_list_widget)
    switch_file_box_state("upload_view")
    cached_data.clear_all_images()


def update_categories(categories_list_widget: Adw.PreferencesGroup, window):
    global added_category_widgets
    

    for widget in added_category_widgets:
        categories_list_widget.remove(widget)
        

    added_category_widgets.clear()
    
    for category in cached_data.categories_list:    
        new_category_widget = CategoryListItem(category_name=category, win=window)
        new_category_widget.connect("category-deleted", lambda b:update_categories(categories_list_widget, window))
        categories_list_widget.add(new_category_widget)
        added_category_widgets.append(new_category_widget)

def create_new_category_dialog_fun(window: Adw.ApplicationWindow, categories_list_widget: Adw.PreferencesGroup):
    dialog = CreateCategoryDialog(
        on_completion=lambda: update_categories(categories_list_widget, window)
    )

    dialog.present(window)
    



def on_activate(app):
    win = Adw.ApplicationWindow(application=app, title="Flagmaster.me Toolkit")
    win.set_default_size(1000,750)

# HOTKEYS
    def open_images_action(action, parameter):
        initial_image_file_picker(win)

    open_images_action_var = Gio.SimpleAction.new("open_images", None)
    open_images_action_var.connect("activate", open_images_action)
    app.add_action(open_images_action_var)

    # Ctrl+O
    app.set_accels_for_action(
        "app.open_images",
        ["<Primary>O"]
    )

    def print_debug_action(action, parameter):
        debug.print_debug()

    print_debug_action_var = Gio.SimpleAction.new("print_debug", None)
    print_debug_action_var.connect("activate", print_debug_action)
    app.add_action(print_debug_action_var)

    # Ctrl+D
    app.set_accels_for_action(
        "app.print_debug",
        ["<Primary>D"]
    )
    


# Body content    
    content = Gtk.Box(
        orientation=Gtk.Orientation.HORIZONTAL,
        hexpand=True,
        vexpand=True
    )


# LEFT CONTENT
    left_content = Gtk.Box(
        orientation=Gtk.Orientation.VERTICAL,
        hexpand=True,
        vexpand=True
    )
    left_content.set_margin_bottom(10)
    left_content.set_margin_start(10)
    left_content.set_margin_end(10)


# File picker Stack
    upload_stack_view = Gtk.Box(
        orientation=Gtk.Orientation.VERTICAL,
        hexpand=True,
        vexpand=True,
        valign = Gtk.Align.CENTER,
        spacing=20, 
    )

    file_picker_button = Gtk.Button(
        label="Upload Images",
        halign=Gtk.Align.CENTER
    )
    file_picker_icon = Gtk.Image.new_from_icon_name("insert-image")
    file_picker_icon.set_pixel_size(100)
    # file_picker_button.set_child(file_picker_icon)
    file_picker_button.connect("clicked", lambda b:(
        initial_image_file_picker(win),
        )
    )
    # file_picker_button.set_size_request(100,100)

    upload_stack_view.append(file_picker_icon)
    upload_stack_view.append(file_picker_button)





# List Stack
# Bottom button row
    images_buttons_box = Gtk.Box(
        hexpand=True,
        spacing=10
    )
# add image button
    add_images_button = Gtk.Button(
        label="Add Additional Images",
        hexpand=True
        )
    add_images_button.add_css_class("suggested-action")
    add_images_button.connect("clicked", lambda b:initial_image_file_picker(win))
# clear image button
    clear_images_button = Gtk.Button(
        label="Clear Loaded Images",
        hexpand=True
        )
    clear_images_button.add_css_class("destructive-action")
    clear_images_button.connect("clicked", lambda b:clear_images())

    images_buttons_box.append(add_images_button)
    images_buttons_box.append(clear_images_button)


    file_stack_view = Gtk.Box(
        orientation= Gtk.Orientation.VERTICAL,
        spacing= 10
    )

    scroll_window_widget = Gtk.ScrolledWindow()
    scroll_window_widget.set_vexpand(True)
    scroll_window_widget.set_hexpand(True)

    scroll_window_widget.set_child(image_list_widget)

    file_stack_view.append(scroll_window_widget)
    file_stack_view.append(images_buttons_box)




# Loading Stack
    loading_stack_view = Gtk.Box(
        orientation=Gtk.Orientation.VERTICAL,
        hexpand=True,
        vexpand=True,
        valign = Gtk.Align.CENTER,
        spacing=20,    
    )

    # loading_spinner = Gtk.Spinner()
    # loading_spinner.set_size_request(100,100)
    # loading_spinner.start()

    loading_text = Gtk.Label(label="Loading Images...")
    loading_text.add_css_class("title-1")
    loading_stack_view.append(
        loading_text
    )




# Compile both stacks
    adw_left_stack.add_titled(title="Upload", child= upload_stack_view, name="upload_view")
    adw_left_stack.add_titled(title="Loading Images", child= loading_stack_view, name="loading_view")
    adw_left_stack.add_titled(title="Files", child= file_stack_view, name="file_view")

# add the stack to the left content
    left_content.append(
        adw_left_stack
    )








# RIGHT CONTENT
    right_content = Gtk.Box(
        orientation=Gtk.Orientation.VERTICAL,
        hexpand=True,
        vexpand=True,
        spacing=20
    )
    

    right_content.set_margin_bottom(10)
    right_content.set_margin_start(10)
    right_content.set_margin_end(10)



# Top section, catagories
    categories_section = Gtk.ScrolledWindow(
        vexpand=True,
        hexpand=True
    )
    
    categories_list_box = Adw.PreferencesGroup(
        hexpand=True,
        vexpand=True,
        title="Categories",
        description="Image Categories"
    )
    
    # categories_list_box.add(debug_list3)
    suffix_button = Gtk.Button(
        label="Suffix",
        icon_name="list-add-symbolic",
        valign=Gtk.Align.CENTER,
    )
    suffix_button.connect("clicked", lambda b:create_new_category_dialog_fun(win, categories_list_box))
    suffix_button.add_css_class("flat")
    categories_list_box.set_header_suffix(suffix=suffix_button)

    categories_section.set_child(categories_list_box)


# Export Settings, Middle
    export_section = Gtk.Box(
        orientation=Gtk.Orientation.HORIZONTAL,
        hexpand=True,
        spacing=10
    ) 

    export_location_box = Gtk.Box(
        orientation=Gtk.Orientation.HORIZONTAL,
        hexpand=True,    
    )

    export_text_field = Gtk.Entry(
        hexpand=True,
        placeholder_text="Export Path"
    )

    export_location_button = Gtk.Button(
        icon_name="folder-open",
        has_tooltip=True,
        tooltip_text="Choose Export Location"
    ) 
    export_location_button.connect("clicked", lambda b:file_location_picker(export_text_field, win))

    export_location_box.add_css_class("linked")
    export_location_box.append(export_text_field)
    export_location_box.append(export_location_button)


    export_section.append(export_location_box)

# Bottom, Button row
    snapshot_row = Gtk.Box(
        orientation=Gtk.Orientation.HORIZONTAL,
        hexpand=True,
        spacing=10
    )

    import_snapshot_button = Gtk.Button(
        label="Import Snapshot",
        hexpand=True
    )
    import_snapshot_button.connect("clicked", lambda b:import_snapshot(window=win, on_completion= lambda: (update_file_stack(image_list_widget), update_categories(categories_list_widget=categories_list_box, window=win))))

    export_snapshot_button = Gtk.Button(
        label="Export Snapshot",
        hexpand=True
    )
    export_snapshot_button.connect("clicked", lambda b:export_snapshot(window=win))


    snapshot_row.append(import_snapshot_button)
    snapshot_row.append(export_snapshot_button)


    compile_button = Gtk.Button(
        label="Compile",
        hexpand=True
    )

    compile_button.connect("clicked", lambda b:image_compiler_class.ImageCompiler(
        output_path=export_text_field.get_text()
    ))

    compile_button.add_css_class("suggested-action")
    compile_button.set_size_request(-1, 100)

    
    bottom_section = Gtk.Box(
        orientation=Gtk.Orientation.VERTICAL,
        hexpand=True,
        spacing=10
    )

    bottom_section.append(
        snapshot_row
    )
    bottom_section.append(
        compile_button
    )





#  compile right side
    separator = Gtk.Separator(
        orientation=Gtk.Orientation.HORIZONTAL
    )
    right_content.append(
        categories_section
    )
    right_content.append(
        separator
    )

    right_content.append(
        export_section
    )
    # separator2 = Gtk.Separator(
    #     orientation=Gtk.Orientation.HORIZONTAL
    # )

    # right_content.append(
    #     separator2
    # )
    right_content.append(
        bottom_section
    )
    
# add the left and the right side to the content area
    vertical_separator = Gtk.Separator(
        orientation=Gtk.Orientation.VERTICAL
    )
    content.append(left_content)
    content.append(vertical_separator)
    content.append(right_content)

# Compile header and body
    toolbar_view = Adw.ToolbarView()
    header = Adw.HeaderBar()
    toolbar_view.add_top_bar(header)
    toolbar_view.set_content(content)
    left_content.set_size_request(1, -1)
    right_content.set_size_request(1, -1)
    toast_overlay.set_child(toolbar_view)
    win.set_content(toast_overlay)
    


#  Hotkeys

    # compile?
    win.present()


def main():
    app = Adw.Application(application_id="me.flagmaster.toolkit")
    app.connect("activate", on_activate)
    app.run(None)

if __name__ == "__main__":
    main()