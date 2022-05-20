from pathlib import Path
from typing import Tuple
from openpyxl import load_workbook as _load_workbook
from openpyxl.workbook.workbook import Workbook

EXCEL_FILE_ENDINGS = ["xlsx"]
RDF_FILE_ENDINGS = {
    ".ttl": "ttl",
    ".rdf": "xml",
    ".xml": "xml",
    ".json-ld": "json-ld",
    ".json": "json-ld",
    ".nt": "nt",
    ".n3": "n3",
}
KNOWN_FILE_ENDINGS = [str(x) for x in RDF_FILE_ENDINGS.keys()] + EXCEL_FILE_ENDINGS
KNOWN_TEMPLATE_VERSIONS = ["0.2.1", "0.3.0", "0.4.0", "0.4.1", "0.4.2", "0.4.3"]
LATEST_TEMPLATE = KNOWN_TEMPLATE_VERSIONS[-1]


class ConversionError(Exception):
    pass


def load_workbook(file_path: Path) -> Workbook:
    if not file_path.name.lower().endswith(tuple(EXCEL_FILE_ENDINGS)):
        raise ValueError("Files for conversion to RDF must be Excel files ending .xlsx")
    return _load_workbook(filename=str(file_path), data_only=True)


def load_template(file_path: Path) -> Workbook:
    if not file_path.name.lower().endswith(tuple(EXCEL_FILE_ENDINGS)):
        raise ValueError(
            "Template files for RDF-to-Excel conversion must be Excel files ending .xlsx"
        )
    if get_template_version(load_workbook(file_path)) != LATEST_TEMPLATE:
        raise ValueError(
            f"Template files for RDF-to-Excel conversion must be of latest version ({LATEST_TEMPLATE})"
        )
    return _load_workbook(filename=str(file_path), data_only=True)


def get_template_version(wb: Workbook) -> str:
    # try 0.4.0 location
    try:
        intro_sheet = wb["Introduction"]
        if intro_sheet["J11"].value in KNOWN_TEMPLATE_VERSIONS:
            return intro_sheet["J11"].value
    except Exception:
        pass

    # try 0.2.1 & 0.3.0 locations
    try:
        # older template version
        pi = wb["program info"]
        if pi["B2"].value in KNOWN_TEMPLATE_VERSIONS:
            return pi["B2"].value
    except Exception:
        pass

    # if we get here, the template version is either unknown or can't be located
    raise Exception(
        "The version of the Excel template you are using cannot be determined"
    )


def split_and_tidy(cell_value: str):
    # note this may not work in list of things that contain commas. Need to consider revising
    # to allow comma-seperated values where it'll split in commas but not in things enclosed in quotes.
    if cell_value == "" or cell_value is None:
        return []
    return (
        [x.strip() for x in cell_value.strip().split(",")]
        if cell_value is not None
        else []
    )


def string_is_http_iri(s: str) -> Tuple[bool, str]:
    # returns (True, None) if the string (sort of) is an IRI
    # returns (False, message) otherwise
    messages = []
    if not s.startswith("http"):
        messages.append("HTTP IRIs must start with 'http' or 'https'")

    if " " in s:
        messages.append("IRIs cannot contain spaces")

    if len(messages) > 0:
        return False, " and ".join(messages)
    else:
        return True, ""


def all_strings_in_list_are_iris(l_: []) -> Tuple[bool, str]:
    messages = []
    if l_ is not None:
        for item in l_:
            r = string_is_http_iri(item)
            if not r[0]:
                messages.append(f"Item {item} failed with messages {r[1]}")

    if len(messages) > 0:
        return False, " and ".join(messages)
    else:
        return True, ""
