import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, Gdk, GLib
toast_overlay = Adw.ToastOverlay()
def warn_user_of_error(error_message: str):
    error_toast = Adw.Toast(
        title=error_message
    )

    error_toast.set_timeout(2)
    error_toast.set_priority(Adw.ToastPriority.HIGH)
    # error_toast.add_css_class("error")  # 👈 red styling
    toast_overlay.add_toast(error_toast)
