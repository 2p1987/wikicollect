import os
import subprocess
from pathlib import Path

from yaml import safe_load


def find_repo_root():
    return (
        subprocess.check_output(["git", "rev-parse", "--show-toplevel"])
        .strip()
        .decode("utf-8")
    )


def load_yaml(file_path: Path):
    with open(file_path, "r") as f:
        file = safe_load(f)
    return file


def return_path_if_exists(path: Path) -> Path:
    if path.exists():
        return path
    else:
        raise ValueError(f"Path {path} does not exist.")


def retrieve_filename_from_path(path: Path) -> str:
    base_name, _ = os.path.splitext(path.name)
    return base_name
