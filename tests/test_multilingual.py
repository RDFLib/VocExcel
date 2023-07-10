import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.absolute()))
from pathlib import Path

from rdflib import Graph

from vocexcel import convert

tests_dir_path = Path(__file__).parent


def test_countrycodes():
    convert.excel_to_rdf(
        tests_dir_path / "030_languages.xlsx",
        output_file_path=tests_dir_path / "030_languages.ttl",
    )

    # file eg-languages-valid.ttl should have been created
    g = Graph().parse(tests_dir_path / "030_languages.ttl")
    assert len(g) == 4940

    # clean up
    Path.unlink(tests_dir_path / "030_languages.ttl", missing_ok=True)
