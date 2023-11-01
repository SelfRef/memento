from threading import Thread
import time
from typing import Callable, List
import os, json
from unidecode import unidecode

try:
	import easyocr
	reader = easyocr.Reader(['pl','en'], gpu=True) # this needs to run only once to load the model into memory
except ModuleNotFoundError:
	print('[W] EasyOCR not installed, OCR functionality will not be available')

def get_list_of_files(path: str, types: None | List[str] = None) -> List[str]:
	file_paths = []
	for root, dirs, files in os.walk(path):
		dirs[:] = [d for d in dirs if not d.startswith('.')]
		for file in files:
			file_path = os.path.join(root, file)
			if (types is None):
				file_paths.append(file_path)
			else:
				if os.path.splitext(file_path)[1] in types:
					file_paths.append(file_path)
	return file_paths

# # TODO: Move to a class
def _scan_ocr_thread(path: str, callback: Callable[[], List[str]]):
	print('[I] Start OCR process')
	words = []
	for word in reader.readtext(path, detail=0):
		for subword in word.split():
			words.append(unidecode(subword.strip().lower()))
	print(f'[I] Found words: {words}')
	callback(words)
	dir_path, filename = os.path.split(path)
	meta_path = os.path.join(dir_path, '.cache', filename + '.json')
	try:
		# TODO: Rewrite to avoid overwriting entire cache file
		with open(meta_path, 'w') as file:
			json.dump({'tags': words}, file)
	except IOError as e:
		print(f'[E] Failed to save cache file: "{meta_path}"', e.strerror)

def scan_ocr_image(path: str, callback: Callable[[], List[str]]):
	Thread(target=_scan_ocr_thread, args=(path, callback)).start()