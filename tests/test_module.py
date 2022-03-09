import pytest

from pathlib import Path
import sys
from rdflib import Graph, URIRef, Literal, compare
from rdflib.namespace import SKOS

sys.path.append(str(Path(__file__).parent.parent.absolute()))
from vocexcel import convert
from vocexcel.utils import ConversionError


def test_exhaustive():
    # convert.excel_to_rdf(
    #     Path(__file__).parent / "040_exhaustive_example.xlsx", output_type="file"
    # )
    # g0 = Graph().parse("040_exhaustive_example.ttl")
    g1 = Graph().parse("040_exhaustive_example_perfect_output.ttl")
    g2 = convert.excel_to_rdf(
        Path(__file__).parent / "040_exhaustive_example.xlsx", output_type="graph"
    )
    # testing differences using algebra -> going through the dictionary and removing any similarities
    g3 = g1 - g2
    print(g3.serialize())
    g4 = g2 - g1
    print(g4.serialize())
    assert compare.isomorphic(g1, g2), "Graphs are not Isomorphic"
    # Path(Path(__file__).parent / "040_exhaustive_example.ttl").unlink()


def test_minimal():
    convert.excel_to_rdf(
        Path(__file__).parent / "040_minimal_example.xlsx", output_type="file"
    )
    g = Graph().parse("040_minimal_example.ttl")
    Path(Path(__file__).parent / "040_minimal_example.ttl").unlink()
