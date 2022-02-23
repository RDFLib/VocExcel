import pytest
try:
    from vocexcel import convert
except:
    import sys

    sys.path.append("..")
    from vocexcel import convert


from pathlib import Path
from rdflib import Graph


def test_baddata_poor_additional_concepts_example():
    with pytest.raises(Exception) as exc_info:
        convert.excel_to_rdf(
                Path(__file__).parent / "baddata.xlsx",
                output_type="file",)

def test_simple():
    convert.excel_to_rdf(
            Path(__file__).parent / "baddata.xlsx",
            output_type="file",)

