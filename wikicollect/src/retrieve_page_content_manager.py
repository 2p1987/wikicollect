from pathlib import Path
from typing import Any, Dict, List

import structlog
import wikipediaapi
from tqdm import tqdm

from wikicollect.src import utils as ut

log = structlog.get_logger()


class ListResultPages:
    """
    A class used to manage and filter search results.

    Attributes:
        metadata_path (Path): The path to the metadata file.
        blacklist_path (Path): The path to the blacklist file.
        searches_folder (Path): The path to the folder containing search results.
        filtered_search_results (Dict[str, List[Dict[str, Any]]]): A collection
        of filtered search results.

    Methods:
        create_filtered_search_results():
            Loads the search results and blacklist, and filters the blacklisted
              pages.
        load_search_results():
            Loads the search results from the searches_folder.
        load_blacklist():
            Loads the blacklist from the blacklist_path.
        filter_blacklisted_pages():
            Filters out the blacklisted pages from the search results.

    Properties:
        results:
            Returns the filtered search results.
    """

    def __init__(
        self, metadata_path: Path, blacklist_path: Path, searches_folder: Path
    ) -> None:
        """
        Constructs all the necessary attributes for the ListResultPages object.

        Args:
            metadata_path (Path): The path to the metadata file.
            blacklist_path (Path): The path to the blacklist file.
            searches_folder (Path): The path to the folder containing search
             results.
        """
        self.metadata_path = metadata_path
        self.blacklist_path = blacklist_path
        self.searches_folder = searches_folder
        self.filtered_search_results = None

    def create_filtered_search_results(self) -> None:
        """Loads the search results and blacklist, and filters the blacklisted
        pages."""
        self.load_search_results()
        log.info("Search results loaded.")
        self.load_blacklist()
        log.info("Black list loaded.")
        self.filter_blacklisted_pages()
        log.info("Search results filtered.")

    def load_search_results(self) -> None:
        """Loads the search results from the searches_folder."""
        searches_path = [file for file in self.searches_folder.glob("*.yaml")]
        if len(searches_path) == 0:
            raise ValueError("Not searches have been performed yet.")
        self.searches_results = {
            ut.retrieve_filename_from_path(results): ut.load_yaml(results)
            for results in searches_path
        }

    def load_blacklist(self) -> None:
        """Loads the blacklist from the blacklist_path."""
        self.blacklist = ut.load_yaml(self.blacklist_path)

    def filter_blacklisted_pages(self) -> None:
        """Filters out the blacklisted pages from the search results."""
        filtered_search_results = {}
        for search_term, results in self.searches_results.items():
            filtered_results = [
                result
                for result in results
                if result["page_name"] not in self.blacklist[search_term]
            ]
            filtered_search_results[search_term] = filtered_results
        self.filtered_search_results = filtered_search_results

    # TODO: do a waterfall deduplication based on the page_ids
    # collect pages ids in the filtered results (count dict?)
    # if page_id already exist when results are screened, do not take into
    # account the result

    @property
    def results(self) -> Dict[str, List[Dict[str, Any]]]:
        """Returns the filtered search results."""
        return self.filtered_search_results


class ExportTextFromWiki:
    """
    A class used to export text content from Wikipedia based on search results.

    Attributes:
        wiki_username (str): Username for Wikipedia API.
        language (str): Language for the Wikipedia content.
        search_results (ListResultPages): Object containing search results to
        retrieve content for.
        wiki_wiki (wikipediaapi.Wikipedia): Wikipedia API instance.

    Class Variables:
        output_path (Path): Default path to store exported content.

    Methods:
        retrieve_page(page_name: str) -> wikipediaapi.WikipediaPage:
            Retrieves the Wikipedia page for a given page name.
        export_page_title_and_text(wiki_page, page_name: str) -> str:
            Constructs a string representation of a Wikipedia page with its
            title and text content.
        retrieve_search_concatenated_text(search_term: str) -> str:
            Concatenates the text of all Wikipedia pages related to a search
            term.
        export_concatenated_text(text: str, text_output_path: Path) -> None:
            Writes the concatenated text to a specified file.
        retrieve_and_export_content(search_term: str) -> None:
            Retrieves and exports the concatenated text for a given search
            term.
    """

    output_path = Path("wikicollect/data")

    def __init__(
        self,
        wiki_username: str,
        language: str,
        search_results: ListResultPages,
    ) -> None:
        """
        Constructs all the necessary attributes for the ExportTextFromWiki
        object.

        Args:
            wiki_username (str): Username for Wikipedia API.
            language (str): Language for the Wikipedia content.
            search_results (ListResultPages): Object containing search results
            to retrieve content for.
        """
        self.wiki_username = wiki_username
        self.language = language
        self.search_results = search_results
        self.wiki_wiki = wikipediaapi.Wikipedia(
            user_agent=self.wiki_username,
            language=self.language,
            extract_format=wikipediaapi.ExtractFormat.WIKI,
        )

    def _retrieve_page(self, page_name: str) -> wikipediaapi.WikipediaPage:
        """
        Retrieves the Wikipedia page for a given page name.

        Args:
            page_name (str): The name of the Wikipedia page.

        Returns:
            wikipediaapi.WikipediaPage: The Wikipedia page object.
        """
        return self.wiki_wiki.page(page_name)

    def _export_page_title_and_text(self, wiki_page, page_name: str) -> str:
        """
        Constructs a string representation of a Wikipedia page with its title
        and text content.

        Args:
            wiki_page (wikipediaapi.WikipediaPage): The Wikipedia page object.
            page_name (str): The name of the Wikipedia page.

        Returns:
            str: The formatted string containing the page title and text.
        """
        return (
            "<s>\n"
            + page_name.replace("_", " ").upper()
            + "\n\n"
            + wiki_page.text
            + "</s>\n"
        )

    def _retrieve_search_concatenated_text(self, search_term: str) -> str:
        """
        Concatenates the text of all Wikipedia pages related to a search term.

        Args:
            search_term (str): The search term to retrieve content for.

        Returns:
            str: The concatenated text of all related Wikipedia pages.
        """
        pages = ""
        for result in tqdm(self.search_results.results[search_term]):
            wiki_page = self._retrieve_page(result["page_name"])
            text_to_concat = self._export_page_title_and_text(
                wiki_page, result["page_name"]
            )
            pages = pages + text_to_concat
        return pages

    def _export_concatenated_text(
        self,
        text: str,
        text_output_path: Path,
    ) -> None:
        """
        Writes the concatenated text to a specified file.

        Args:
            text (str): The text content to write.
            text_output_path (Path): The path to the file to write the text to.
        """
        with open(text_output_path, "w") as f:
            f.write(text)

    def retrieve_and_export_content(self, search_term: str) -> None:
        """
        Retrieves and exports the concatenated text for a given search term.

        Args:
            search_term (str): The search term to retrieve and export content
            for.

        Raises:
            ValueError: If the output file already exists.
        """
        text_output_path = Path(self.output_path, f"{search_term}.txt")
        if text_output_path.exists():
            raise ValueError(f"Text output already exists at {text_output_path}")
        log.info(f"Retrieving content for search term {search_term}")
        pages = self._retrieve_search_concatenated_text(search_term)
        self._export_concatenated_text(pages, text_output_path)
        log.info(f"Export finished to {text_output_path}")
