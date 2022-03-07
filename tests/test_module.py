import pytest

from pathlib import Path
import sys
from rdflib import Graph, URIRef, Literal, compare
from rdflib.namespace import SKOS

sys.path.append(str(Path(__file__).parent.parent.absolute()))
from vocexcel import convert
from vocexcel.utils import ConversionError


def test_exhaustive():
    convert.excel_to_rdf(
        Path(__file__).parent / "040_exhaustive_example.xlsx", output_type="file"
    )
    g = Graph().parse("040_exhaustive_example.ttl")

    # print(g)
    # g2 = convert.excel_to_rdf(
    #     Path(__file__).parent / "040_exhaustive_example.xlsx", output_type="graph"
    # )
    # print("++++++++++++++++++++++:))")
    # print(g2)
    # print("--------------------------------")
    # compare.isomorphic(g, g2)
    Path(Path(__file__).parent / "040_exhaustive_example.ttl").unlink()


def test_minimal():
    convert.excel_to_rdf(
        Path(__file__).parent / "040_minimal_example.xlsx", output_type="file"
    )
    g = Graph().parse("040_minimal_example.ttl")
    Path(Path(__file__).parent / "040_minimal_example.ttl").unlink()
