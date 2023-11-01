import json
from os import path

# This implementation is temporary, will be replaced with GtkSettings
class Settings():
	def __init__(self) -> None:
		self._dir_path = path.split(__file__)[0]
		self._file_name = 'settings.json'
		self._all_settings: dict = {}
		self._load()

	@property
	def last_meme_directory(self):
		return self._all_settings.get('last_meme_directory', None)

	@last_meme_directory.setter
	def last_meme_directory(self, value: str | None):
		self._all_settings['last_meme_directory'] = value
		self._save()

	def _load(self):
		try:
			settings_path = path.join(self._dir_path, self._file_name)

			if not path.exists(settings_path):
				print('[W] Settings file not found')
				return

			with open(settings_path, 'r') as file:
				self._all_settings = json.load(file)

		except IOError:
			print('[E] Cannot read settings file')

	def _save(self):
		try:
			settings_path = path.join(self._dir_path, self._file_name)

			with open(settings_path, 'w') as file:
				json.dump(self._all_settings, file)

		except IOError:
			print('[E] Cannot read settings file')