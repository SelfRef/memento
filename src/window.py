from typing import List
import gi, os
from PIL import Image
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GObject, Gdk, GLib, GdkPixbuf
from models import GifPaintable, MemeItem, MemeStore

@Gtk.Template(filename='ui/main.ui')
class Window(Adw.ApplicationWindow):
	__gtype_name__ = "Window"

	iconSize: int = 150
	thumbnailWidgets: List[Gtk.Picture] = []
	filePaths: List[str] = []
	store: MemeStore = MemeStore()
	selected_directory: str
	default_view: str = 'no_memes'
	# default_view = 'loading'

	iconSizeScale: Gtk.Scale = Gtk.Template.Child()
	imgGrid: Gtk.GridView = Gtk.Template.Child()
	noMemesStatus: Adw.StatusPage = Gtk.Template.Child()
	main_stack: Gtk.Stack = Gtk.Template.Child()
	progress: Gtk.ProgressBar = Gtk.Template.Child()
	overlay_sidebar: Adw.OverlaySplitView = Gtk.Template.Child()

	def __init__(self, app):
		super().__init__(application=app, default_height=600, default_width=800, title='Memento')
		self.main_stack.set_visible_child_name(self.default_view)
		self.present()

		ptbl = GifPaintable('ui/travolta.gif')
		self.noMemesStatus.set_paintable(ptbl)

		gridModel = Gtk.NoSelection(model=self.store)
		gridFactory = Gtk.SignalListItemFactory()
		gridFactory.connect('setup', self.setup_grid_view_item_factory)
		gridFactory.connect('bind', self.bind_grid_view_item_factory)

		self.imgGrid.set_model(gridModel)
		self.imgGrid.set_factory(gridFactory)


	def load_memes(self, dir_path: str):
		self.main_stack.set_visible_child_name('loading')
		self.store.load_folder(dir_path, self.memes_loaded, self.progress)

	def memes_loaded(self):
		self.main_stack.set_visible_child_name('memes')
		self.iconSizeScale.set_sensitive(True)

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
		modelItem: MemeItem = item.get_item()
		picture: Gtk.Picture = item.get_child()
		path = modelItem.thumb_path
		img: Image.Image = modelItem.image
		if img is not None:
			print(f'[I] Loading from memory: "{modelItem.path}')
			try:
				pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(
					GLib.Bytes.new(img.tobytes()),
					GdkPixbuf.Colorspace.RGB,
					False,
					8,
					img.width,
					img.height,
					img.width * 3
				)
				picture.set_paintable(Gdk.Texture.new_for_pixbuf(pixbuf))
			except:
				print(f'[E] Failed loading from memory: "{modelItem.path}')
		else:
			print(f'[W] Fallback loading from name: "{modelItem.path}')
			picture.set_filename(path)
		#pic.set_filename('ui/test.png')

	@Gtk.Template.Callback()
	def change_icon_size(self, wgt: Gtk.Scale, *args):
		iconSize = int(wgt.get_value() * 50)
		for pic in self.thumbnailWidgets:
			pic.set_size_request(iconSize, iconSize)

	@Gtk.Template.Callback()
	def generate_thumbnails(self, *_):
		print('test')

	@Gtk.Template.Callback()
	def select_directory(self, *_):
		picker = Gtk.FileDialog(title="Select your meme directory")

		def set_selected_directory(dialog: Gtk.FileDialog, result):
			file: Gio.File = dialog.select_folder_finish(result)
			self.load_memes(file.get_path())

		picker.select_folder(self, callback=set_selected_directory)

	@Gtk.Template.Callback()
	def test(self, *_):
		val = self.overlay_sidebar.get_show_sidebar()
		self.overlay_sidebar.set_show_sidebar(not val)