from typing import List
import os

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