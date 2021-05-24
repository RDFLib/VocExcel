from sys import path
from pathlib import Path
path.append(str(Path(__file__).parent.parent))
import argparse
from vocexcel import profiles, convert, __version__


def convert_file(excel_file_path: Path):
    pass


def main(args=None):
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "-v",
        "--version",
        help="The version of this copy of VocExel.",
        action="store_true"
    )

    parser.add_argument(
        "-lp",
        "--listprofiles",
        help="This flag, if set, must be the only flag supplied. It will cause the program to list all the vocabulary"
        " profiles that this converter, indicating both their URI and their short token for use with the"
        " -p (--profile) flag when converting Excel files",
        action="store_true",
    )

    parser.add_argument(
        "excel_file",
        type=Path,
        help="The Excel file to convert to a SKOS vocabulary in RDF",
    )

    parser.add_argument(
        "-val",
        "--validate",
        help="Validate output file",
        action="store_true"
    )

    parser.add_argument(
        "-p",
        "--profile",
        help="A profile - a specified information model - for a vocabulary. This tool understands several profiles and"
             "you can choose which one you want to convert the Excel file according to. The list of profiles - URIs "
             "and their corresponding tokens - supported by VocExcel, can be found by running the program with the "
             "flag -lp or --listprofiles.",
        default="vocpub",
    )

    args = parser.parse_args()

    if args.listprofiles:
        print(profiles.list_profiles())
        exit()
    elif args.version:
        print(__version__)
        exit()
    elif args.excel_file:
        print(f"Processing file {args.excel_file}")


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
