from os import listdir, rename, makedirs
from os.path import isfile, join, islink, exists
from pathlib import Path
from typing import List, Tuple, Union, Generator


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

    def _walk_and_return_path(self, dirs: Union[dict, list]) -> Tuple[List[str], list]:
        if type(dirs) is list:
            return [], dirs

        for k in dirs.keys():
            path, val = self._walk_and_return_path(dirs[k])
            ret = [k]
            ret.extend(path)
            return ret, val

    def _path_generator(self, dirs: dict) -> Union[Generator, None]:
        if type(dirs) is not dict:
            return
        for k in dirs.keys():
            path, files = self._walk_and_return_path(dirs[k])
            ret_path = [k]
            ret_path.extend(path)
            yield ret_path, files

    def restructure_directory(self, cur_path: str, suggestions: dict):
        for new_dir, files in self._path_generator(suggestions):
            for file in files:
                new_path = join(cur_path, *new_dir)
                if not exists(new_path):
                    makedirs(new_path)
                rename(join(cur_path, file), join(new_path, file))
