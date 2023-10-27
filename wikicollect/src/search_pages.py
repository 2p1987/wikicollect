import argparse
from pathlib import Path

import requests
import yaml

# TODO: add logging


def search_wikipedia(srsearch, srlimit=100, language="en"):
    SEARCH_API_URL = f"https://{language}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": srsearch,
        "srlimit": srlimit,
    }

    response = requests.get(url=SEARCH_API_URL, params=params)
    data = response.json()
    search_result = data["query"]["search"]
    transformed_search_results = [
        {
            "page_name": item["title"].replace(" ", "_"),
            "page_id": item["pageid"],
            "size": item["size"],
            "word_count": item["wordcount"],
        }
        for item in search_result
    ]
    metadata_directory = Path("data/metadata/searches")
    metadata_directory.mkdir(parents=True, exist_ok=True)
    with open(Path(metadata_directory, f"""{params["srsearch"]}.yaml"""), "w") as f:
        yaml.dump(transformed_search_results, f, default_flow_style=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search Wikipedia and save metadata.")
    parser.add_argument("srsearch", type=str, help="Search term for Wikipedia.")
    parser.add_argument(
        "--srlimit",
        type=int,
        default=100,
        help="Limit for search results. Default is 100.",
    )
    parser.add_argument(
        "--language",
        type=str,
        default="en",
        help="Language for search. Default is 'en'.",
    )

    args = parser.parse_args()

    search_wikipedia(args.srsearch, args.srlimit, args.language)
