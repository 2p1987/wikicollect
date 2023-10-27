import argparse
import os
from importlib import reload
from pathlib import Path

from wikicollect.src import utils as ut
from wikicollect.src.retrieve_page_content_manager import (
    ExportTextFromWiki,
    ListResultPages,
)

reload(ut)

# ---- Constants

METADATA_FOLDER = ut.return_path_if_exists(Path("wikicollect/data/metadata"))
SEARCHES_FOLDER = ut.return_path_if_exists(Path(METADATA_FOLDER, "searches"))
BLACKLIST_PATH = ut.return_path_if_exists(Path(METADATA_FOLDER, "page_blacklist.yaml"))

if WIKI_USERNAME := os.environ.get("WIKI_USERNAME"):
    pass
else:
    raise ValueError("Missing WIKI_USERNAME in environment variables")


def retrieve_page_content(search_term: str, language: str):
    search_term = search_term.replace(" ", "_")
    # --- Create filtered searches results

    list_result_page = ListResultPages(METADATA_FOLDER, BLACKLIST_PATH, SEARCHES_FOLDER)
    list_result_page.create_filtered_search_results()

    # --- Extract content from Wiki

    export_text_from_wiki = ExportTextFromWiki(
        WIKI_USERNAME, language, list_result_page
    )
    export_text_from_wiki.retrieve_and_export_content(search_term)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Retrieve and export wikipedia text related to a search term"
    )
    parser.add_argument(
        "search_term", type=str, help="Search term to extract text from."
    )
    parser.add_argument(
        "--language",
        type=str,
        default="en",
        help="Language for search. Default is 'en'.",
    )

    args = parser.parse_args()

    retrieve_page_content(args.search_term, args.language)
