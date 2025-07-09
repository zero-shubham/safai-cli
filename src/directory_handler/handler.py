from os import listdir, rename, makedirs
from os.path import isfile, join, islink, exists
from pathlib import Path
from typing import List


class DirectoryHandler:
    def __init__(self, path: Path, ignore: List[str]):
        self.root_path = path
        self.ignore = ignore

    def list_directory_files(self, recursive: bool = False, path: str = "") -> dict:
        cur_path = join(self.root_path, path)

        if isfile(cur_path) or islink(cur_path):
            return {}

        for ig in self.ignore:
            if ig in cur_path:
                return {}

        dir_content = listdir(cur_path)
        extracted_files = {cur_path: []}
        for f in dir_content:
            if isfile(join(self.root_path, path, f)) or islink(
                join(self.root_path, path, f)
            ):
                extracted_files[cur_path].append(f)
            elif recursive:
                extracted_files.update(
                    self.list_directory_files(path=join(path, f), recursive=recursive)
                )

        return extracted_files

    def restructure_directory(self, path: str, suggestions: dict):
        for new_dir, files in suggestions.items():
            for file in files:
                new_path = join(path, new_dir)
                if not exists(new_path):
                    makedirs(new_path)
                rename(join(path, file), join(new_path, file))
