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
