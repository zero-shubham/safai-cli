from os import listdir, rename
from os.path import isfile, join, islink


class DirectoryHandler:
    def __init__(self, path: str):
        self.root_path = path.removesuffix("/")

    def list_directory_files(self, recursive: bool = False, path: str = "") -> dict:
        if isfile(join(self.root_path, path)) or islink(join(self.root_path, path)):
            return {}

        dir_content = listdir(join(self.root_path, path))
        extracted_files = {join(self.root_path, path): []}
        for f in dir_content:
            if isfile(join(self.root_path, path, f)) or islink(
                join(self.root_path, path, f)
            ):
                extracted_files[join(self.root_path, path)].append(f)
            elif recursive:
                extracted_files.update(
                    self.list_directory_files(path=join(path, f), recursive=recursive)
                )

        return extracted_files

    def restructure_directory(self, path: str, suggestions: dict):
        for new_dir, files in suggestions.items():
            for file in files:
                pass
