import sys
from pydantic import ValidationError
from models import Configuration


class ConfigLoader:
    """Handles loading, comment-stripping, and validation of config files."""

    def __init__(self, filename: str) -> None:
        """Initialize the loader with a target file path.

        Args:
            filename (str): Path to the JSON configuration file.
        """
        self._filename: str = filename

    def load(self) -> Configuration:
        """Load and return the validated Configuration.

        Returns:
            Configuration: Validated configuration or safe default fallback.
        """
        self._validate_extension()
        raw_content = self._read_file_without_comments()
        return self._parse_json(raw_content)

    def _validate_extension(self) -> None:
        """Ensure the target configuration file is a .json file."""
        if not self._filename.endswith(".json"):
            print(
                f"Error: '{self._filename}' is not a valid .json file.",
                file=sys.stderr,
            )
            sys.exit(1)

    def _read_file_without_comments(self) -> str:
        """Read the file content while stripping comment lines starting with #.

        Returns:
            str: JSON string without comments.
        """
        try:
            with open(self._filename, mode="r", encoding="utf-8") as f:
                return "".join(
                    line for line in f if not line.strip().startswith("#")
                )
        except OSError as err:
            print(
                f"Error: Unable to read file '{self._filename}': {err}",
                file=sys.stderr,
            )
            sys.exit(1)

    def _parse_json(self, json_str: str) -> Configuration:
        """Validate JSON string against the Configuration model.

        Args:
            json_str (str): Cleaned JSON text.

        Returns:
            Configuration: Validated model or fallback instance.
        """
        try:
            return Configuration.model_validate_json(json_str)
        except (ValidationError, Exception) as err:
            print(
                f"Warning: Configuration invalid ({err}). "
                f"Using default configuration.",
                file=sys.stderr,
            )
            return Configuration()
