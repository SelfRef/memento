from threading import Thread
import time
from typing import Callable, List
import os, json
# import easyocr

# # TODO: Move to a class
# ocr_reader = easyocr.Reader(['en', 'pl'])

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


def _scan_ocr_thread(path: str, callback: Callable[[], List[str]]):
	time.sleep(3)
	callback(['a', 'b', 'c'])


# def _scan_ocr_thread(path: str, callback: Callable[[], List[str]]):
#		words = []
# 	for word in ocr_reader.readtext(path):
#			adddddddd with unidecode
# 	callback(words)
# 	dir_path, filename = os.path.split(path)
# 	meta_path = os.path.join(dir_path, '.cache', filename, '.json')
# 	try:
# 		# TODO: Rewrite to avoid overwriting entire cache file
# 		with open(meta_path, 'w') as file:
# 			json.dump({'tags': words}, file)
# 	except IOError as e:
# 		print(f'[E] Failed to save cache file: "{meta_path}"', e.strerror)

def scan_ocr_image(path: str, callback: Callable[[], List[str]]):
	print('start ocr')
	Thread(target=_scan_ocr_thread, args=(path, callback)).start()