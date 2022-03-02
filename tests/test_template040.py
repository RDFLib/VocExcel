import pytest

from pathlib import Path
import sys
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import SKOS

sys.path.append(str(Path(__file__).parent.parent.absolute()))
from vocexcel import convert
from vocexcel.utils import ConversionError


def test_simple():
    convert.excel_to_rdf(
        Path(__file__).parent / "040_simple_valid.xlsx", output_type="file"
    )
    g = Graph().parse("040_simple_valid.ttl")
    assert len(g) == 111
    assert (
        URIRef(
            "http://resource.geosciml.org/classifierscheme/cgi/2016.01/particletype"
        ),
        SKOS.prefLabel,
        Literal("Particle Type", lang="en"),
    ) in g, "PrefLabel for vocab is not correct"
    # tidy up
    Path("040_simple_valid.ttl").unlink()


def test_complex():
    convert.excel_to_rdf(
        Path(__file__).parent / "040_complex_valid.xlsx", output_type="file"
    )
    g = Graph().parse("040_complex_valid.ttl")
    assert len(g) == 111
    assert (
        URIRef(
            "http://resource.geosciml.org/classifierscheme/cgi/2016.01/particletype"
        ),
        SKOS.prefLabel,
        Literal("Particle Type", lang="en"),
    ) in g, "PrefLabel for vocab is not correct"
    # tidy up
    Path("040_complex_valid.ttl").unlink()


def test_empty_template():
    assert Path(
        Path(__file__).parent.parent / "templates" / "VocExcel-template_040.xlsx"
    ).is_file()
    with pytest.raises(ConversionError) as e:
        convert.excel_to_rdf(
            Path(__file__).parent.parent / "templates" / "VocExcel-template_040.xlsx",
            output_type="file",
        )
    assert "7 validation errors for ConceptScheme" in str(e)


# this includes code for testing invlaid template
# def test_invalid_template():
#     convert.excel_to_rdf(
#         Path(__file__).parent / "040_complexexample_invalid.xlsx", output_type="file"
#     )
#     g = Graph().parse("040_complexexample_invalid.ttl")
#     assert (
#                URIRef(
#                    "http://resource.geosciml.org/classifierscheme/cgi/2016.01/particletype"
#                ),
#                SKOS.prefLabel,
#                Literal("Particle Type", lang="en"),
#            ) in g, "PrefLabel for vocab is not correct"
#     # tidy up
#     Path("040_complex_valid.ttl").unlink()
