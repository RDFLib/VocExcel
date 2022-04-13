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


def extract_concepts_and_collections(
        s: Worksheet,
) -> Tuple[List[models.Concept], List[models.Collection]]:
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
                            pl_language_code=split_and_tidy(
                                s[f"C{row}"].value
                            ),  # new in 0.3.0
                            alt_labels=split_and_tidy(s[f"D{row}"].value),
                            definition=s[f"E{row}"].value,
                            def_language_code=split_and_tidy(
                                s[f"F{row}"].value
                            ),  # new in 0.3.0
                            children=split_and_tidy(s[f"G{row}"].value),
                            other_ids=split_and_tidy(s[f"H{row}"].value),
                            home_vocab_uri=s[f"I{row}"].value,
                            provenance=s[f"J{row}"].value,
                            template_version="0.3.0",
                        )

                        concepts.append(c)
                    except ValidationError as e:
                        raise ConversionError(
                            f"Concept processing error likely at column {col}, row {row}, and has error: {e}"
                        )
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
                            provenance=s[f"E{row}"].value,
                        )
                        collections.append(c)
                    except ValidationError as e:
                        raise ConversionError(
                            f"Collection processing error, likely at row {row}, error: {e}"
                        )
            elif cell.value is None:
                pass

    return concepts, collections


def extract_concept_scheme(sheet: Worksheet):
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
    return cs
