from pathlib import Path
from typing import Literal, Optional, Union

from googleapiclient.discovery import build
from pydantic import ValidationError

try:
    import models, profiles
    from utils import split_and_tidy_to_strings, ConversionError
except:
    import sys

    sys.path.append("..")
    from vocexcel import models, profiles
    from vocexcel.convert import validate_with_profile, log_msg
    from vocexcel.utils import (
        split_and_tidy_to_strings,
        ConversionError,
        validate_with_profile,
        log_msg,
    )

ACCEPTED_TEMPLATE_VERSIONS = ["0.4.3"]
SPREADSHEET_ID = None
RANGE = None
KEY = None
client = None
sheet = None


def get_spreadsheetid_from_URI(uri: str) -> str:
    try:
        split = uri.split("/d/")
        split2 = split[1].split("/edit")
        spreadsheetid = split2[0]
    except Exception:
        raise Exception("There seems to be something wrong with the URI supplied")
    return spreadsheetid


def only_one_colon_in_str(string: str):
    counter = 0
    for character in string:
        if character == ":":
            counter += 1
    if counter != 1:
        return False
    return True


def using_prefix_list_output(cell_value: list, prefix: dict):
    variables = []
    for i in cell_value:
        if cell_value is not None:
            try:
                c = i
                if c.startswith("http"):
                    pass
                elif only_one_colon_in_str(i):
                    split_c_prefix = c.split(":")[0]
                    split_c_added_component = c.split(":")[1]

                    if split_c_prefix in prefix:
                        c = prefix[split_c_prefix] + split_c_added_component
                    else:
                        print(
                            f"The prefix used: {split_c_prefix} isn't included in the prefix sheet"
                        )
                        raise Exception
                else:
                    print(
                        f"Something doesn't look right with this cell_value {cell_value}. "
                        f"Likely this isn't in http form or more colons are used than normal"
                    )
                    raise Exception
                variables.append(c)
            except Exception as e:
                print(e)
                exit(1)
    return variables


def using_prefix_non_list_output(cell_value, prefix: dict):
    c = cell_value
    if c is not None:
        if c.startswith("http"):
            pass
        elif only_one_colon_in_str(c):
            split_c_prefix = c.split(":")[0]
            split_c_added_component = c.split(":")[1]

            if split_c_prefix in prefix:
                c = prefix[split_c_prefix] + split_c_added_component
            else:
                print(
                    f"The prefix used: '{split_c_prefix}' isn't included in the prefix sheet"
                )
                raise Exception
        else:
            print(
                f"Something doesn't look right with the cell value: {cell_value}. "
                f"Likely this isn't in http form or more colons are used than normal"
            )
            raise Exception
    return c


def get_template_version_gsheets(spreadsheet_id: str):
    # Load workbook
    try:
        intro_sheet = (
            sheet.values()
            .get(spreadsheetId=spreadsheet_id, range="Introduction!J11")
            .execute()
        )
        template_value = intro_sheet.get("values")[0][0]
        return template_value
    except Exception:
        raise Exception(
            "The version of the Google Template you are using is not accepted/can't be determined"
        )


def read_cell(sheet_dict: dict, n: int, i: Optional[int] = 0):
    try:
        if sheet_dict.get("values")[n]:
            return sheet_dict.get("values")[n][i]
        else:
            return None
    except IndexError:
        return None


def rows_filled_out(c_sheet: dict):
    variable = len(c_sheet.get("values"))
    return variable


def create_prefix_dict(prefix_s: dict):
    prefix_dict = {}
    for index in range(1, rows_filled_out(prefix_s)):
        try:
            prefix_dict[read_cell(prefix_s, index, 0)] = read_cell(prefix_s, index, 1)
        except Exception as e:
            f"Prefix Processing Error, at the prefix sheet, row: {index}, {e}"
    return prefix_dict


def extract_concept_scheme(concept_scheme_sheet: dict, prefix: dict):
    cs = models.ConceptScheme(
        uri=using_prefix_non_list_output(read_cell(concept_scheme_sheet, 0), prefix),
        title=read_cell(concept_scheme_sheet, 1),
        description=read_cell(concept_scheme_sheet, 2),
        created=read_cell(concept_scheme_sheet, 3),
        modified=read_cell(concept_scheme_sheet, 4),
        creator=read_cell(concept_scheme_sheet, 5),
        publisher=read_cell(concept_scheme_sheet, 6),
        version=read_cell(concept_scheme_sheet, 7),
        provenance=read_cell(concept_scheme_sheet, 8),
        custodian=read_cell(concept_scheme_sheet, 9),
        pid=read_cell(concept_scheme_sheet, 10),
    )
    return cs


def extract_concepts(
    concepts_sheet: dict, additional_concepts_sheet: dict, prefix: dict
):
    concepts = []
    for index in range(2, rows_filled_out(concepts_sheet)):
        try:
            c = models.Concept(
                uri=using_prefix_non_list_output(
                    read_cell(concepts_sheet, index, 0), prefix
                ),
                pref_label=read_cell(concepts_sheet, index, 1),
                pl_language_code=split_and_tidy_to_strings(
                    read_cell(concepts_sheet, index, 2)
                ),
                definition=read_cell(concepts_sheet, index, 3),
                def_language_code=split_and_tidy_to_strings(
                    read_cell(concepts_sheet, index, 4)
                ),
                alt_labels=split_and_tidy_to_strings(
                    read_cell(concepts_sheet, index, 5)
                ),
                children=using_prefix_list_output(
                    split_and_tidy_to_strings(read_cell(concepts_sheet, index, 6)),
                    prefix,
                ),
                provenance=read_cell(concepts_sheet, index, 7),
                home_vocab_uri=using_prefix_non_list_output(
                    read_cell(concepts_sheet, index, 8), prefix
                ),
                # additional concepts sheet page
                related_match=using_prefix_list_output(
                    split_and_tidy_to_strings(
                        read_cell(additional_concepts_sheet, index, 0)
                    ),
                    prefix,
                ),
                close_match=using_prefix_list_output(
                    split_and_tidy_to_strings(
                        read_cell(additional_concepts_sheet, index, 1)
                    ),
                    prefix,
                ),
                exact_match=using_prefix_list_output(
                    split_and_tidy_to_strings(
                        read_cell(additional_concepts_sheet, index, 2)
                    ),
                    prefix,
                ),
                narrow_match=using_prefix_list_output(
                    split_and_tidy_to_strings(
                        read_cell(additional_concepts_sheet, index, 3)
                    ),
                    prefix,
                ),
                broad_match=using_prefix_list_output(
                    split_and_tidy_to_strings(
                        read_cell(additional_concepts_sheet, index, 4)
                    ),
                    prefix,
                ),
            )
            concepts.append(c)
        except ValidationError as e:
            raise ConversionError(
                f" Concept Processing error likely at sheet 'Concepts*' or 'Additional Concept Features', "
                f"row {index + 1}, and has {e} "
            )
    return concepts


def extract_collections(collection_sheet: dict, prefix: dict):
    collections = []
    row = rows_filled_out(collection_sheet)
    for index in range(2, row):
        try:
            c = models.Collection(
                uri=using_prefix_non_list_output(
                    read_cell(collection_sheet, index, 0), prefix
                ),
                pref_label=read_cell(collection_sheet, index, 1),
                definition=read_cell(collection_sheet, index, 2),
                members=using_prefix_list_output(
                    split_and_tidy_to_strings(read_cell(collection_sheet, index, 3)),
                    prefix,
                ),
                provenance=read_cell(collection_sheet, index, 4),
            )
            collections.append(c)
        except ValidationError as e:
            raise ConversionError(
                f" Collection Processing Error likely at the 'Collections' sheet, row {row}, and has {e}"
            )
    return collections


def excel_to_rdf_gsheets(
    uri: str,
    key: str,
    file_to_convert_path: Path,
    output_type: Literal["file", "string", "graph"] = "file",
    output_file_path=None,
    output_format: Literal["turtle", "xml", "json-ld"] = "turtle",
    profile="vocpub",
    error_level=1,
    message_level=1,
    log_file=None,
    validate=False,
):
    # get spreadsheet id from uri
    global SPREADSHEET_ID
    SPREADSHEET_ID = get_spreadsheetid_from_URI(uri)

    global KEY
    KEY = key

    global client
    client = build("sheets", "v4", developerKey=KEY)

    global sheet
    sheet = client.spreadsheets()

    # Template Version Validation
    template_version = get_template_version_gsheets(SPREADSHEET_ID)
    if template_version not in ACCEPTED_TEMPLATE_VERSIONS:
        raise ValueError(
            f"Unknown Template Version. Known Template Versions for Google Sheets are "
            f"{', '.join(ACCEPTED_TEMPLATE_VERSIONS)}, however you supplied {template_version}"
        )

    # Template Version 0.4.3
    if template_version == "0.4.3":
        try:
            concept_scheme_sheet = (
                sheet.values()
                .get(spreadsheetId=SPREADSHEET_ID, range="Concept Scheme*!B2:B12")
                .execute()
            )
            concept_sheet = (
                sheet.values()
                .get(spreadsheetId=SPREADSHEET_ID, range="Concepts*!A:I")
                .execute()
            )
            additional_concept_sheet = (
                sheet.values()
                .get(
                    spreadsheetId=SPREADSHEET_ID,
                    range="Additional Concept Features!B:F",
                )
                .execute()
            )
            collection_sheet = (
                sheet.values()
                .get(spreadsheetId=SPREADSHEET_ID, range="Collections!A:E")
                .execute()
            )
            prefix_sheet = (
                sheet.values()
                .get(spreadsheetId=SPREADSHEET_ID, range="Prefix Sheet!A:B")
                .execute()
            )

            prefix = create_prefix_dict(prefix_sheet)
            concept_scheme = extract_concept_scheme(concept_scheme_sheet, prefix)
            concept = extract_concepts(concept_sheet, additional_concept_sheet, prefix)
            collections = extract_collections(collection_sheet, prefix)
        except Exception as e:
            print(e)

    # Build the total vocab
    vocab_graph = models.Vocabulary(
        concept_scheme=concept_scheme, concepts=concept, collections=collections
    ).to_graph()

    # validate with vocpub
    if validate:
        validate_with_profile(
            vocab_graph,
            profile=profile,
            error_level=error_level,
            message_level=message_level,
            log_file=log_file,
        )

    # Write out the file
    if output_type == "graph":
        return vocab_graph
    elif output_type == "string":
        return vocab_graph.serialize(format=output_format)
    else:  # output_format == "file":
        if output_file_path is not None:
            dest = output_file_path
        else:
            if output_format == "xml":
                suffix = ".rdf"
            elif output_format == "json-ld":
                suffix = ".json-ld"
            else:
                suffix = ".ttl"
            dest = file_to_convert_path.with_suffix(suffix)
        vocab_graph.serialize(destination=str(dest), format=output_format)
        return dest


if __name__ == "__main__":
    pass
