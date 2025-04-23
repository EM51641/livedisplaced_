import argparse
from typing import Optional, Sequence

import yaml  # type: ignore


def main(argv: Optional[Sequence[str]] = None) -> object:
    """
    Parse attached arguments
    """

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-v",
        "--version",
        help="show program's version",
        action="store_true",
    )

    parser.add_argument(
        "-c",
        "--init_tables",
        help="create and initialise database",
        action="store_true",
    )

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = main()

    if getattr(args, "version"):
        with open("config.yaml", "r") as f:
            data = yaml.safe_load(f)
            version = data["app"]["version"]
        print(version)

    if getattr(args, "init_tables"):
        print("db initialized")
