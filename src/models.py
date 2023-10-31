from concurrent.futures import ThreadPoolExecutor
from os import path, mkdir
from pickletools import optimize
from queue import Empty, Queue
from threading import Thread
from typing import Callable, List
from gi.repository import GLib, Gdk, GdkPixbuf, GObject, Gio, Gtk
from utils import get_list_of_files
from PIL import Image

class MemeStore(Gio.ListStore):
	def __init__(self):
		super().__init__(item_type=MemeItem)
		self.savingQueue = Queue()

	def load_folder(self, dir_path: str, callback: Callable[[], None], progress: Gtk.ProgressBar):
		td = Thread(target=self.loading_folder, args=(dir_path, callback, progress))
		td.start()

	def loading_folder(self, dir_path: str, callback: Callable[[], None], progress: Gtk.ProgressBar):
		filePaths = get_list_of_files(dir_path, ['.png', '.jpg'])
		self.create_meme_items(filePaths, progress)
		callback()

	def create_meme_items(self, filePaths: List[str], progress: Gtk.ProgressBar):
		all_len = len(filePaths)
		for index, path in enumerate(filePaths):
			thumbPath, img = self.generate_thumbnail(path)
			self.append(MemeItem(path, thumbPath, img))
			progress.set_fraction(index/all_len)
		# Thread(target=self.save_thumbnail_queue).start()

	def generate_thumbnail(self, itemPath: str) -> (str, Image.Image):
		dir, filename = path.split(itemPath)
		thumbPath = path.join(dir, '.thumbnails', filename + '.cache')

		img: Image.Image = None
		if path.exists(thumbPath):
			print(f'[I] Thumbnail already generated for "{itemPath}"')
			img = Image.open(thumbPath)
		else:
			img = Image.open(itemPath)
			img.thumbnail((200, 200))
			img = img.convert('RGB')
			self.savingQueue.put((img, thumbPath))
		return (thumbPath, img)

	def save_thumbnail_queue(self):
		while True:
			try:
				img, thumbPath = self.savingQueue.get()
			except Empty:
				continue
			else:
				try:
					thumbDir = path.join(dir, '.thumbnails')
					if not path.exists(thumbDir):
						mkdir(thumbDir)
					img.save(thumbPath, 'JPEG', optimize=True)
					print(f'[O] Generated and saved thumbnail to "{thumbPath}"')
				finally:
					self.savingQueue.task_done()

class MemeItem(GObject.Object):
	def __init__(self, path: str, thumbPath: str, image: Image) -> None:
		super().__init__()
		self._path: str = path
		self._thumb_path: str = thumbPath
		self._image: Image = image

	@GObject.Property(type=str)
	def path(self):
		return self._path

	@GObject.Property(type=str)
	def thumb_path(self):
		return self._thumb_path

	@property
	def image(self):
		return self._image

	@thumb_path.setter
	def thumb_path(self, value):
		self._thumb_path = value
		self.notify('thumb_path')

class GifPaintable(GObject.Object, Gdk.Paintable):
	'''Version of Paintable that works with GIFs.\n
	Stolen from https://discourse.gnome.org/t/python-how-do-you-implement-a-paintable-for-gif-animations/16054/4'''
	def __init__(self, path):
		super().__init__()
		self.animation = GdkPixbuf.PixbufAnimation.new_from_file(path)
		self.iterator = self.animation.get_iter()
		self.delay = self.iterator.get_delay_time()
		self.timeout = GLib.timeout_add(self.delay, self.on_delay)

		self.invalidate_contents()

	def on_delay(self):
		delay = self.iterator.get_delay_time()
		self.timeout = GLib.timeout_add(delay, self.on_delay)
		self.invalidate_contents()

		return GLib.SOURCE_REMOVE

	def do_get_intrinsic_height(self):
		return self.animation.get_height()

	def do_get_intrinsic_width(self):
		return self.animation.get_width()

	def invalidate_contents(self):
		self.emit("invalidate-contents")

	def do_snapshot(self, snapshot, width, height):
		timeval = GLib.TimeVal()
		timeval.tv_usec = GLib.get_real_time()
		self.iterator.advance(timeval)
		pixbuf = self.iterator.get_pixbuf()
		texture = Gdk.Texture.new_for_pixbuf(pixbuf)

		texture.snapshot(snapshot, width, height)