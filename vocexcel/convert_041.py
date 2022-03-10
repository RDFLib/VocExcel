from typing import Tuple, List

from openpyxl.worksheet.worksheet import Worksheet
from pydantic import ValidationError

try:
    import models
    from utils import split_and_tidy, ConversionError
except:
    import sys

    sys.path.append("..")
    from vocexcel import models
    from vocexcel.utils import split_and_tidy, ConversionError


# this is a new function to iterate over the collection sheet in template version 0.4.1
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
                        pl_language_code=split_and_tidy(q[f"C{row}"].value),
                        definition=q[f"D{row}"].value,
                        def_language_code=split_and_tidy(q[f"E{row}"].value),
                        alt_labels=split_and_tidy(q[f"F{row}"].value),
                        children=split_and_tidy(q[f"G{row}"].value),
                        provenance=q[f"H{row}"].value,
                        # Note in the new template, home_vocab_uri is synonymous with source vocab uri
                        home_vocab_uri=q[f"I{row}"].value,
                        # additional concept features sheets
                        related_match=split_and_tidy(r[f"B{row}"].value),
                        close_match=split_and_tidy(r[f"C{row}"].value),
                        exact_match=split_and_tidy(r[f"D{row}"].value),
                        narrow_match=split_and_tidy(r[f"E{row}"].value),
                        broad_match=split_and_tidy(r[f"F{row}"].value),
                    )
                    concepts.append(c)
                except ValidationError as e:
                    raise ConversionError(
                        f"Concept processing error, row {row}, error: {e}"
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
                        members=split_and_tidy(s[f"D{row}"].value),
                        provenance=s[f"E{row}"].value,
                    )
                    collections.append(c)
                except ValidationError as e:
                    raise ConversionError(
                        f"Collection processing error, row {row}, error: {e}"
                    )
    return concepts, collections
