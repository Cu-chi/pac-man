"""Configuration loader module."""
import sys
from pydantic import ValidationError
from models import Configuration


def load_config(filename: str) -> Configuration:
    """Load, clean, and validate the configuration file.

    Args:
        filename (str): Path to the config file.

    Returns:
        Configuration: Validated Configuration model.
    """
    if not filename.endswith(".json"):
        print(f"Error: '{filename}' is not a valid .json file.",
              file=sys.stderr)
        sys.exit(1)

    try:
        with open(filename, mode="r", encoding="utf-8") as f:
            json_no_comments = "".join(
                line for line in f if not line.strip().startswith("#")
            )
    except OSError as err:
        print(f"Error: Unable to read file '{filename}': {err}",
              file=sys.stderr)
        sys.exit(1)

    try:
        return Configuration.model_validate_json(json_no_comments)
    except (ValidationError, Exception) as err:
        print(f"Warning: Configuration invalid ({err}). "
              f"Using default configuration.", file=sys.stderr)
        return Configuration()
