from typing import List
import gi, os
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio

def get_list_of_files(path: str, types: None | List[str] = None) -> List[str]:
	file_paths = []
	for root, dirs, files in os.walk(path):
		for file in files:
			file_path = os.path.join(root, file)
			if (types is None):
				file_paths.append(file_path)
			else:
				if os.path.splitext(file_path)[1] in types:
					file_paths.append(file_path)
	return file_paths

def setup_grid_view_item_factory(factory: Gtk.SignalListItemFactory, item: Gtk.ListItem):
	pic = Gtk.Picture(
		height_request=200,
		width_request=200,
		margin_bottom=10,
		margin_end=10,
		margin_start=10,
		margin_top=10)
	item.set_child(pic)

def bind_grid_view_item_factory(factory: Gtk.SignalListItemFactory, item: Gtk.ListItem):
	pic: Gtk.Picture = item.get_child()
	path: str = item.get_item().get_string()
	pic.set_filename(path)
	#pic.set_filename('ui/test.png')


def on_activate(app):
	builder: Gtk.Builder = Gtk.Builder.new_from_file("./ui/main.ui")
	view = builder.get_object('mainView')
	window = Adw.ApplicationWindow(content=view, default_width=800, default_height=600, title='Memento')
	window.set_application(app)
	window.present()

	filePaths = get_list_of_files('/home/selfref/Pictures/memes-bak', ['.png', '.jpg'])
	model = Gtk.StringList(strings=filePaths)
	gridModel = Gtk.NoSelection(model=model)
	gridFactory = Gtk.SignalListItemFactory()
	gridFactory.connect('setup', setup_grid_view_item_factory)
	gridFactory.connect('bind', bind_grid_view_item_factory)

	grid: Gtk.GridView = builder.get_object('imgGrid')
	grid.set_model(gridModel)
	grid.set_factory(gridFactory)

app = Adw.Application(application_id='org.gtk.Example')
app.connect('activate', on_activate)
app.run(None)



