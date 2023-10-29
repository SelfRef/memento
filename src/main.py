import gi, os

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

def on_activate(app):
	builder: Gtk.Builder = Gtk.Builder.new_from_file("./ui/meme-gallery.ui")
	window: Gtk.Window = builder.get_object('main')
	window.set_application(app)
	window.present()

	flow: Gtk.FlowBox = builder.get_object('flow')

	for img in os.listdir('./assets'):
		pic = Gtk.Picture()
		pic.set_filename(os.path.join('assets', img))
		flowchild = Gtk.FlowBoxChild()
		flowchild.set_child(pic)
		flow.append(flowchild)

app = Gtk.Application(application_id='org.gtk.Example')
app.connect('activate', on_activate)
app.run(None)