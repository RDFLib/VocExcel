import argparse
from pathlib import Path
from typing import List, Tuple
from typing import Literal

from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException
from openpyxl.worksheet.worksheet import Worksheet
from pydantic.error_wrappers import ValidationError

import models
import profiles
from __init__ import __version__


def split_and_tidy(cell_value: str):
    return [x.strip() for x in cell_value.strip().split(",")] if cell_value is not None else None


def extract_concepts_and_collections(s: Worksheet) -> Tuple[List[models.Concept], List[models.Collection]]:
    concepts = []
    collections = []
    process_concept = False
    process_collection = False
    for col in s.iter_cols(max_col=1):
        for cell in col:
            row = cell.row
            if cell.value == "Concept URI":
                process_concept = True
            elif cell.value == "Collection URI":
                process_concept = False
                process_collection = True
            elif process_concept:
                if cell.value is None:
                    pass
                else:
                    try:
                        c = models.Concept(
                            uri=s[f"A{row}"].value,
                            pref_label=s[f"B{row}"].value,
                            alt_labels=split_and_tidy(s[f"C{row}"].value),
                            definition=s[f"D{row}"].value,
                            children=split_and_tidy(s[f"E{row}"].value),
                            other_ids=split_and_tidy(s[f"F{row}"].value),
                            home_vocab_uri=s[f"G{row}"].value,
                            provenance=s[f"H{row}"].value
                        )
                        concepts.append(c)
                    except ValidationError as e:
                        print(f"On Row {row}:")
                        print(e)
                        exit()
            elif process_collection:
                if cell.value is None:
                    pass
                else:
                    try:
                        c = models.Collection(
                            uri=s[f"A{row}"].value,
                            pref_label=s[f"B{row}"].value,
                            definition=s[f"C{row}"].value,
                            members=split_and_tidy(s[f"D{row}"].value),
                            provenance=s[f"E{row}"].value
                        )
                        collections.append(c)
                    except ValidationError as e:
                        print(f"On Row {row}:")
                        print(e)
                        exit()
            elif cell.value is None:
                pass

    return concepts, collections


def convert_file(excel_file_path: Path, sheet_name=None, output_format: Literal["file", "string", "graph"] = "file"):
    wb = None
    try:
        wb = load_workbook(filename=str(excel_file_path), data_only=True)
        sheet = wb["vocabulary" if sheet_name is None else sheet_name]

        # Vocabulary
        try:
            cs = models.ConceptScheme(
                uri=sheet["B1"].value,
                title=sheet["B2"].value,
                description=sheet["B3"].value,
                created=sheet["B4"].value,
                modified=sheet["B5"].value,
                creator=sheet["B6"].value,
                publisher=sheet["B7"].value,
                version=sheet["B8"].value,
                provenance=sheet["B9"].value,
                custodian=sheet["B10"].value,
                pid=sheet["B11"].value,
            )
        except ValidationError as e:
            print(e)
            exit()

        # Concepts & Collections
        concepts, collections = extract_concepts_and_collections(sheet)

        # Build the total vocab
        v = models.Vocabulary(concept_scheme=cs, concepts=concepts, collections=collections)

        # Write out the file
        if output_format == "graph":
            return v.to_graph()
        elif output_format == "string":
            return v.to_graph().serialize()
        else:  # output_format == "file":
            dest = excel_file_path.name.replace("xlsx", "ttl")
            print(f"Created vocab RDF file {dest}")
            v.to_graph().serialize(destination=dest)

    except InvalidFileException as e:
        print("You supplied a path to a file that either doesn't exist or isn't an Excel file")


def main(args=None):
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "-v",
        "--version",
        help="The version of this copy of VocExel. Must still set an excel_file value to call this (can be fake)",
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

    parser.add_argument(
        "-of",
        "--outputformat",
        help="The format of the vocabulary output.",
        choices=["file", "string"],
        default="file",
    )

    parser.add_argument(
        "-s",
        "--sheet",
        help="The sheet within the target Excel Workbook to process",
        default="vocabulary",
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

        try:
            o = convert_file(args.excel_file, sheet_name=args.sheet, output_format=args.outputformat)
            if args.outputformat == "string":
                print(o)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
