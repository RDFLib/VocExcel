from typing import List, Tuple

from openpyxl.worksheet.worksheet import Worksheet
from pydantic import ValidationError

try:
    import models
    from utils import ConversionError, split_and_tidy_to_strings
except ImportError:
    import sys

    sys.path.append("..")
    from vocexcel import models
    from vocexcel.utils import ConversionError, split_and_tidy_to_strings


# this is a new function to iterate over the collection sheet in template version 0.4.0
def extract_concepts_and_collections(
    q: Worksheet, r: Worksheet, s: Worksheet
) -> Tuple[List[models.Concept], List[models.Collection]]:
    concepts = []
    collections = []
    # Iterating over the concept page and the additional concept page
    for col in q.iter_cols(max_col=1):
        for cell in col:
            row = cell.row
            if (
                cell.value is None
                or cell.value == "Concepts"
                or cell.value == "Concept IRI*"
            ):
                pass
            else:
                try:
                    c = models.Concept(
                        uri=q[f"A{row}"].value,
                        pref_label=q[f"B{row}"].value,
                        pl_language_code=split_and_tidy_to_strings(q[f"C{row}"].value),
                        definition=q[f"D{row}"].value,
                        def_language_code=split_and_tidy_to_strings(q[f"E{row}"].value),
                        alt_labels=split_and_tidy_to_strings(q[f"F{row}"].value),
                        children=split_and_tidy_to_strings(q[f"G{row}"].value),
                        provenance=q[f"H{row}"].value,
                        home_vocab_uri=q[f"I{row}"].value,
                        # additional concept features sheets
                        related_match=split_and_tidy_to_strings(r[f"B{row}"].value),
                        close_match=split_and_tidy_to_strings(r[f"C{row}"].value),
                        exact_match=split_and_tidy_to_strings(r[f"D{row}"].value),
                        narrow_match=split_and_tidy_to_strings(r[f"E{row}"].value),
                        broad_match=split_and_tidy_to_strings(r[f"F{row}"].value),
                    )
                    concepts.append(c)
                except ValidationError as e:
                    raise ConversionError(
                        f"Concept processing error, likely at sheet {q}, row {row}, and with error: {e}"
                    )

    # iterating over the collections page
    for col in s.iter_cols(max_col=1):
        for cell in col:
            row = cell.row
            if (
                cell.value is None
                or cell.value == "Collections"
                or cell.value == "Collection URI"
            ):
                pass
            else:
                try:
                    c = models.Collection(
                        uri=s[f"A{row}"].value,
                        pref_label=s[f"B{row}"].value,
                        definition=s[f"C{row}"].value,
                        members=split_and_tidy_to_strings(s[f"D{row}"].value),
                        provenance=s[f"E{row}"].value,
                    )
                    collections.append(c)
                except ValidationError as e:
                    raise ConversionError(
                        f"Collection processing error, likely at sheet {s}, column {col}, row {row}, error: {e}"
                    )
    return concepts, collections


def extract_concept_scheme(sheet: Worksheet):
    cs = models.ConceptScheme(
        uri=sheet["B2"].value,
        title=sheet["B3"].value,
        description=sheet["B4"].value,
        created=sheet["B5"].value,
        modified=sheet["B6"].value,
        creator=sheet["B7"].value,
        publisher=sheet["B8"].value,
        version=sheet["B9"].value,
        provenance=sheet["B10"].value,
        custodian=sheet["B11"].value,
        pid=sheet["B12"].value,
    )
    return cs
