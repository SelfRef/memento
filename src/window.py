from typing import List
import gi, os
from PIL import Image
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio
from utils.models import GifPaintable, MemeItem

@Gtk.Template(filename='ui/main.ui')
class Window(Adw.ApplicationWindow):
	__gtype_name__ = "Window"

	iconSize: int = 150
	thumbnailWidgets: List[Gtk.Picture] = []
	filePaths: List[str] = []
	model: Gio.ListStore = Gio.ListStore(item_type=MemeItem)
	selected_directory: str

	iconSizeScale: Gtk.Scale = Gtk.Template.Child()
	imgGrid: Gtk.GridView = Gtk.Template.Child()
	noMemesStatus: Adw.StatusPage = Gtk.Template.Child()
	main_stack: Gtk.Stack = Gtk.Template.Child()

	def __init__(self, app):
		super().__init__(application=app, default_height=600, default_width=800, title='Memento')
		self.present()

		ptbl = GifPaintable('ui/travolta.gif')
		self.noMemesStatus.set_paintable(ptbl)

		gridModel = Gtk.NoSelection(model=self.model)
		gridFactory = Gtk.SignalListItemFactory()
		gridFactory.connect('setup', self.setup_grid_view_item_factory)
		gridFactory.connect('bind', self.bind_grid_view_item_factory)

		self.imgGrid.set_model(gridModel)
		self.imgGrid.set_factory(gridFactory)

	def get_list_of_files(self, path: str, types: None | List[str] = None) -> List[str]:
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

	def setup_grid_view_item_factory(self, factory: Gtk.SignalListItemFactory, item: Gtk.ListItem):
		pic = Gtk.Picture(
			width_request=self.iconSize,
			height_request=self.iconSize,
			margin_bottom=10,
			margin_end=10,
			margin_start=10,
			margin_top=10)

		self.thumbnailWidgets.append(pic)
		item.set_child(pic)

	def bind_grid_view_item_factory(self, factory: Gtk.SignalListItemFactory, item: Gtk.ListItem):
		pic: Gtk.Picture = item.get_child()
		modelItem: MemeItem = item.get_item()
		path = modelItem.path
		pic.set_filename(path)
		#pic.set_filename('ui/test.png')

	@Gtk.Template.Callback()
	def change_icon_size(self, wgt: Gtk.Scale, *args):
		iconSize = int(wgt.get_value() * 50)
		for pic in self.thumbnailWidgets:
			pic.set_size_request(iconSize, iconSize)

	@Gtk.Template.Callback()
	def generate_thumbnails(self, *_):
		print('test')

	def load_folder(self):
		self.filePaths = self.get_list_of_files(self.select_directory, ['.png', '.jpg'])
		for path in self.filePaths:
			self.model.append(MemeItem(path))
		self.main_stack.set_visible_child_name('memes')

	@Gtk.Template.Callback()
	def select_directory(self, *_):
		picker = Gtk.FileDialog(title="Select your meme directory")

		def set_selected_directory(dialog: Gtk.FileDialog, result):
			file: Gio.File = dialog.select_folder_finish(result)
			self.select_directory = file.get_path()
			self.load_folder()

		picker.select_folder(self, callback=set_selected_directory)

	@Gtk.Template.Callback()
	def scan_ocr(self, *_):
		pass