import gi, sys
from PIL import Image
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw
from window import Window

def on_activate(app):
	Window(app)

app = Adw.Application(application_id='org.gtk.Example')
app.connect('activate', on_activate)
app.run(sys.argv)