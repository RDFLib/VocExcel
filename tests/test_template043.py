import sys
from pathlib import Path

import pytest
from rdflib import Graph, URIRef, Literal, compare
from rdflib.namespace import DCTERMS, SKOS, RDF

sys.path.append(str(Path(__file__).parent.parent.absolute()))
from vocexcel import convert
from vocexcel.utils import ConversionError


def test_empty_template():
    with pytest.raises(ConversionError) as e:
        convert.excel_to_rdf(
            Path(__file__).parent.parent / "templates" / "VocExcel-template-043.xlsx"
        )
    assert "7 validation errors for ConceptScheme" in str(e)


def test_simple():
    tests_dir_path = Path(__file__).parent
    g = convert.excel_to_rdf(
        tests_dir_path / "043_simple_valid.xlsx",
        # output_file_path=tests_dir_path /"043_simple_valid_nc.ttl"
        output_format="graph",
    )
    assert (
        URIRef(
            "http://resource.geosciml.org/classifierscheme/cgi/2016.01/particletype"
        ),
        SKOS.prefLabel,
        Literal("Particle Type", lang="en"),
    ) in g, "PrefLabel for vocab is not correct"
    assert (
        URIRef("http://resource.geosciml.org/classifier/cgi/particletype/bioclast"),
        DCTERMS.provenance,
        Literal("NADM SLTTs 2004", lang="en"),
    ) in g, "Provenance for vocab is not correct"


def test_exhaustive_template_is_isomorphic():
    tests_dir_path = Path(__file__).parent
    g1 = Graph().parse(tests_dir_path / "043_exhaustive.ttl")
    g2 = convert.excel_to_rdf(
        Path(__file__).parent / "043_exhaustive.xlsx", output_format="graph"
    )
    assert compare.isomorphic(g1, g2), "Graphs are not Isomorphic"


def test_rdf_to_excel():
    tests_dir_path = Path(__file__).parent
    g1 = Graph().parse(tests_dir_path / "043_exhaustive.ttl")
    convert.rdf_to_excel(
        tests_dir_path / "043_exhaustive.ttl",
        output_file_path=tests_dir_path / "043_exhaustive_roundtrip.xlsx",
    )
    g2 = convert.excel_to_rdf(
        tests_dir_path / "043_exhaustive.xlsx", output_format="graph"
    )

    # clean up files
    Path(tests_dir_path / "043_exhaustive_roundtrip.xlsx").unlink(missing_ok=True)
    assert compare.isomorphic(g1, g2), "Graphs are not Isomorphic"
