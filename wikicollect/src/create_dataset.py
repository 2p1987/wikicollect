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
    data = []

    for file_path in folder_path.glob("*.json"):
        with open(file_path, "r", encoding="utf-8") as f:
            data.extend([json.loads(line) for line in f])

    return DatasetDict({"train": Dataset.from_pandas(pd.DataFrame(data))})


# ---- Main


if __name__ == "__main__":
    # Now you are authenticated and can use the Hugging Face API
    dataset = load_ndjson_to_dataset(DATA_FOLDER)
    log.info(f"Dataset created with {len(dataset)} entries")
    dataset.push_to_hub("pierre-pessarossi/wikipedia-climate-data")
    log.info("Dataset pushed to hub")
