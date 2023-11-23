import json
import os
from importlib import reload
from pathlib import Path

import pandas as pd
import structlog
from datasets import Dataset, DatasetDict

from wikicollect.src import utils as ut

reload(ut)

# set dir to root

os.chdir(ut.find_repo_root())

# get logger
log = structlog.get_logger()


# ---- Constants

DATA_FOLDER = ut.return_path_if_exists(Path("wikicollect/data"))


def load_ndjson_to_dataset(folder_path: Path) -> DatasetDict:
    dataset_dict = {}

    for file_path in folder_path.glob("*.json"):
        with open(file_path, "r", encoding="utf-8") as f:
            data = [json.loads(line) for line in f]
        dataset_dict[file_path.name.replace(".json", "")] = Dataset.from_pandas(
            pd.DataFrame(data)
        )

    return DatasetDict(dataset_dict)


def save_dataset_locally(dataset: DatasetDict, folder_path: Path) -> None:
    dataset.save_to_disk(folder_path)


# ---- Main


if __name__ == "__main__":
    # Now you are authenticated and can use the Hugging Face API
    dataset = load_ndjson_to_dataset(DATA_FOLDER)
    log.info(f"Dataset created with {len(dataset)} entries")
    save_dataset_locally(dataset, Path(DATA_FOLDER, "dataset"))
    log.info("Dataset saved locally")
