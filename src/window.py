import time, gi, os
from typing import List
from PIL import Image
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GObject, Gdk, GLib, GdkPixbuf
from models import GifPaintable, MemeItem, MemeStore, ViewEnum
from settings import Settings

@Gtk.Template(filename='ui/main.ui')
class Window(Adw.ApplicationWindow):
	__gtype_name__ = "Window"

	icon_size_scale: Gtk.Scale = Gtk.Template.Child()
	miniatures_grid_view: Gtk.GridView = Gtk.Template.Child()
	no_memes_status_page: Adw.StatusPage = Gtk.Template.Child()
	main_stack: Gtk.Stack = Gtk.Template.Child()
	preview_stack: Gtk.Stack = Gtk.Template.Child()
	progress_bar: Gtk.ProgressBar = Gtk.Template.Child()
	overlay_sidebar: Adw.OverlaySplitView = Gtk.Template.Child()
	overlay_picture: Gtk.Picture = Gtk.Template.Child()
	button_preview_hide: Gtk.ToggleButton = Gtk.Template.Child()

	preview_info_button: Gtk.ToggleButton = Gtk.Template.Child()
	preview_info_filename: Adw.ActionRow = Gtk.Template.Child()
	preview_info_size: Adw.ActionRow = Gtk.Template.Child()
	preview_info_weight: Adw.ActionRow = Gtk.Template.Child()

	preview_tags_button: Gtk.ToggleButton = Gtk.Template.Child()
	preview_tags_ocr: Adw.ActionRow = Gtk.Template.Child()

	def __init__(self, app, settings: Settings):
		super().__init__(
			application=app,
			default_height=800,
			default_width=1200,
			width_request=500,
			height_request=500,
			title='Memento')
		self.settings: Settings = settings
		self.preview_width = 500
		self.icon_size: int = 150
		self.selected_item: MemeItem | None = None
		self.thumbnailWidgets: List[Gtk.Picture] = []
		self.filePaths: List[str] = []
		self.store: MemeStore = MemeStore()
		self.selected_directory: str
		self.default_view: ViewEnum = ViewEnum.NoMemes
		self.change_stack_view()

		ptbl = GifPaintable('ui/travolta.gif')
		self.no_memes_status_page.set_paintable(ptbl)

		self.last_progress_update_time = time.time()
		self.gridModel = Gtk.SingleSelection(model=self.store, can_unselect=True, autoselect=False)
		self.gridModel.connect('selection-changed', self.open_preview)
		gridFactory = Gtk.SignalListItemFactory()
		gridFactory.connect('setup', self.setup_grid_view_item_factory)
		gridFactory.connect('bind', self.bind_grid_view_item_factory)
		self.miniatures_grid_view.set_factory(gridFactory)

		self.overlay_sidebar.connect('notify::show-sidebar', self.on_preview_panel_switch)
		self.present()

		last_dir = settings.last_meme_directory
		if last_dir and os.path.exists(last_dir):
			self.load_memes(last_dir)

	def on_preview_panel_switch(self, *_):
		if not self.overlay_sidebar.get_show_sidebar():
			self.preview_info_button.set_active(False)

	def open_preview(self, selection: Gtk.SingleSelection, *_):
		self.selected_item = selection.get_selected_item()
		pic = Gdk.Texture.new_from_filename(self.selected_item.path)
		self.overlay_picture.set_paintable(pic)
		self.set_preview_info()

		# This is a workaround for getting scrollable image that's always 100% of parent width
		# Maybe there's a better solution in GTK I haven't found yet
		height_request = pic.get_height() * self.preview_width / pic.get_width()
		self.overlay_picture.set_property('height-request', height_request)

		self.overlay_sidebar.set_show_sidebar(True)
		self.preview_stack.set_visible_child_name('preview')

	def set_preview_info(self):
		self.preview_info_filename.set_subtitle(self.selected_item.filename)
		weight = self.selected_item.weight / 1024000
		self.preview_info_weight.set_subtitle(f'{weight:.2f} MB')
		width, height = self.selected_item.size
		self.preview_info_size.set_subtitle(f'{width}px x {height}px')

	def load_memes(self, dir_path: str):
		self.change_stack_view(ViewEnum.Loading)
		# Seems like GTK behaves more reliable when model is set not set during appending
		self.miniatures_grid_view.set_model(None)
		self.store.load_folder(dir_path, self.memes_loaded, self.update_progress)
		self.settings.last_meme_directory = dir_path

	def memes_loaded(self):
		self.miniatures_grid_view.set_model(self.gridModel)
		self.change_stack_view(ViewEnum.Memes)
		self.icon_size_scale.set_sensitive(True)

	def setup_grid_view_item_factory(self, factory: Gtk.SignalListItemFactory, item: Gtk.ListItem):
		pic = Gtk.Picture(
			width_request=self.icon_size,
			height_request=self.icon_size,
			margin_bottom=10,
			margin_end=10,
			margin_start=10,
			margin_top=10)

		self.thumbnailWidgets.append(pic)
		item.set_child(pic)

	def bind_grid_view_item_factory(self, factory: Gtk.SignalListItemFactory, item: Gtk.ListItem):
		modelItem: MemeItem = item.get_item()
		picture: Gtk.Picture = item.get_child()

		# Potential solution to handle icons click event instead of relying on selection
		# ctrl = Gtk.GestureClick()
		# ctrl.connect('released', lambda *_: self.testevent(modelItem.path))
		# picture.add_controller(ctrl)

		path = modelItem.thumb_path
		img: Image.Image = modelItem.image
		if img is not None:
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

	def update_progress(self, progress: float):
		current_time = time.time()
		# Gtk doesn't like updating progress bar more often
		# it causes a glitch where window becomes empty
		if current_time - self.last_progress_update_time >= 0.5:
			self.progress_bar.set_fraction(progress)
			self.last_progress_update_time = current_time

	def change_stack_view(self, view: ViewEnum | None = None):
		if not view:
			view = self.default_view
		self.main_stack.set_visible_child_name(view.value)
		if view is ViewEnum.Memes:
			self.button_preview_hide.set_visible(True)

	@Gtk.Template.Callback()
	def change_icon_size(self, scale: Gtk.Scale, *_):
		iconSize = int(scale.get_value() * 50)
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