import gi, os
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

def on_activate(app):
	builder: Gtk.Builder = Gtk.Builder.new_from_file("./ui/main.ui")
	view = builder.get_object('mainView')
	window = Adw.ApplicationWindow(content=view, default_width=800, default_height=600)
	window.set_application(app)
	window.present()

app = Adw.Application(application_id='org.gtk.Example')
app.connect('activate', on_activate)
app.run(None)