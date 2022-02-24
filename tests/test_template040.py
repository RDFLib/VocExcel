import pytest
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.absolute()))
from vocexcel import convert


def test_baddata_poor_additional_concepts_example():
    with pytest.raises(Exception) as exc_info:
        convert.excel_to_rdf(
            Path(__file__).parent / "040_baddata.xlsx",
            output_type="file",
        )


def test_simple():
    convert.excel_to_rdf(
        Path(__file__).parent / "040_baddata.xlsx",
        output_type="file",
    )
