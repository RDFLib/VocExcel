import sys
from pathlib import Path

import pytest
from rdflib import Graph, URIRef, Literal, compare
from rdflib.namespace import SKOS

sys.path.append(str(Path(__file__).parent.parent.absolute()))
from vocexcel import convert
from vocexcel.utils import ConversionError

tests_dir_path = Path(__file__).parent


def test_empty_template():
    with pytest.raises(ConversionError) as e:
        convert.excel_to_rdf(
            Path(__file__).parent.parent / "templates" / "VocExcel-template_040.xlsx",
        )
    assert "7 validation errors for ConceptScheme" in str(e)


def test_simple():
    convert.excel_to_rdf(tests_dir_path / "040_simple.xlsx", output_file_path=tests_dir_path / "040_simple.ttl")
    g = Graph().parse(tests_dir_path / "040_simple.ttl")
    assert len(g) == 142
    assert (
        URIRef(
            "http://resource.geosciml.org/classifierscheme/cgi/2016.01/particletype"
        ),
        SKOS.prefLabel,
        Literal("Particle Type", lang="en"),
    ) in g, "PrefLabel for vocab is not correct"
    Path(tests_dir_path / "040_simple.ttl").unlink()


def test_exhaustive_template_is_isomorphic():
    g1 = Graph().parse(tests_dir_path / "040_exhaustive_comparison.ttl")
    g2 = convert.excel_to_rdf(tests_dir_path / "040_exhaustive.xlsx", output_format="graph")
    assert compare.isomorphic(g1, g2), "Graphs are not Isomorphic"


def test_minimal_template_is_isomorphic():
    g1 = Graph().parse(tests_dir_path / "040_minimal_comparison.ttl")
    g2 = convert.excel_to_rdf(tests_dir_path / "040_minimal.xlsx", output_format="graph")
    assert compare.isomorphic(g1, g2), "Graphs are not Isomorphic"
