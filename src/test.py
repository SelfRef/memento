from PIL import Image
import gi
gi.require_version("Gdk", "4.0")
from gi.repository import Gio, Gdk, GObject, GLib, GdkPixbuf

img = Image.open('/home/selfref/Projects/memento/src/ui/test.png')

raw_bytes = img.tobytes()

gbytes = GLib.Bytes.new(raw_bytes)

pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(
	gbytes,
	GdkPixbuf.Colorspace.RGB,
	False,
	8,
	img.width,
	img.height,
	img.width * 3
)

pic = Gdk.Texture.new_for_pixbuf(pixbuf)

