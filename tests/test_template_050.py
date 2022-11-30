import sys
from pathlib import Path

import pytest
from rdflib import Graph, URIRef, Literal, compare, Namespace
from rdflib.namespace import DCTERMS, SKOS, RDF
from textwrap import dedent
sys.path.append(str(Path(__file__).parent.parent.absolute()))
from vocexcel import convert
from vocexcel.utils import ConversionError, load_workbook, expand_namespaces
from vocexcel.convert_050 import extract_prefixes, extract_concept_scheme, extract_concepts


def test_extract_prefixes():
    g = Graph()

    wb = load_workbook(Path(__file__).parent / "050_simple.xlsx")

    n = extract_prefixes(wb["Prefixes"])

    g.add((expand_namespaces("ex:thing-1", n), SKOS.prefLabel, Literal("Thing 1", lang="en")))
    g.add((expand_namespaces("ch:rhode-island-red", n), SKOS.prefLabel, Literal("Rhode Island Red", lang="en")))

    # print(g.serialize(format="longturtle"))
    expected = """
                PREFIX ex: <http://example.com/>
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                
                <http://example.com/chickens/rhode-island-red>
                    skos:prefLabel "Rhode Island Red"@en ;
                .
                
                ex:thing-1
                    skos:prefLabel "Thing 1"@en ;
                .    
                """
    g2 = Graph().parse(data=expected)
    assert compare.isomorphic(g, g2)


def test_extract_concept_scheme():
    wb = load_workbook(Path(__file__).parent / "050_simple.xlsx")
    prefixes = extract_prefixes(wb["Prefixes"])
    cs = extract_concept_scheme(wb["Concept Scheme"], prefixes)

    wb = load_workbook(Path(__file__).parent / "050_simple2.xlsx")
    prefixes = extract_prefixes(wb["Prefixes"])
    cs2 = extract_concept_scheme(wb["Concept Scheme"], prefixes)

    # no IRI
    with pytest.raises(ConversionError) as e:
        wb = load_workbook(Path(__file__).parent / "050_simple_invalid.xlsx")
        prefixes = extract_prefixes(wb["Prefixes"])
        extract_concept_scheme(wb["Concept Scheme"], prefixes)

    # IRI starts with unknown prefix
    with pytest.raises(ConversionError) as e:
        wb = load_workbook(Path(__file__).parent / "050_simple_invalid2.xlsx")
        prefixes = extract_prefixes(wb["Prefixes"])
        extract_concept_scheme(wb["Concept Scheme"], prefixes)

    # no created date
    with pytest.raises(ConversionError) as e:
        wb = load_workbook(Path(__file__).parent / "050_simple_invalid3.xlsx")
        prefixes = extract_prefixes(wb["Prefixes"])
        extract_concept_scheme(wb["Concept Scheme"], prefixes)


def test_extract_concepts():
    wb = load_workbook(Path(__file__).parent / "050_simple.xlsx")
    prefixes = extract_prefixes(wb["Prefixes"])
    cons = extract_concepts(wb["Concepts"], prefixes)
    expected = '''PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX ex: <http://example.com/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

ex:bantam
    a skos:Concept ;
    dcterms:source "https://en.wikipedia.org/wiki/Bantam_(poultry)"^^xsd:anyURI ;
    skos:definition "A bantam is any small variety of fowl, usually of chicken or duck."@en ;
    skos:narrower ex:silkie ;
    skos:prefLabel "Bantam"@en ;
.

ex:rhode-island-red
    a skos:Concept ;
    dcterms:provenance "Taken from Wikipedia" ;
    dcterms:source "https://en.wikipedia.org/wiki/Rhode_Island_Red"^^xsd:anyURI ;
    skos:definition """The Rhode Island Red is an American breed of domestic chicken. It is the state bird of Rhode Island."""@en ;
    skos:prefLabel "Rhode Island Red"@en ;
.

ex:silkie
    a skos:Concept ;
    skos:altLabel "Silky, Chinese silk chicken"@en ;
    skos:definition "The Silkie (also known as the Silky or Chinese silk chicken) is a breed of chicken named for its atypically fluffy plumage, which is said to feel like silk and satin."@en ;
    skos:prefLabel "Silkie"@en ;
.
'''
    g2 = Graph().parse(data=expected)
    assert compare.isomorphic(cons, g2)
    # print((g2 - cons).serialize(format="longturtle"))
    # print("++++++++++++++")
    # print((cons - g2).serialize(format="longturtle"))

    # print(cons.serialize(format="longturtle"))


def test_empty_template():
    with pytest.raises(ConversionError) as e:
        convert.excel_to_rdf(Path(__file__).parent.parent / "templates" / "VocExcel-template_050.xlsx")
    assert "7 validation errors for ConceptScheme" in str(e)


def test_simple():
    tests_dir_path = Path(__file__).parent
    g = convert.excel_to_rdf(
        tests_dir_path / "043_simple_valid.xlsx",
        # output_file_path=tests_dir_path /"043_simple_valid_nc.ttl"
        output_format="graph"
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
    g2 = convert.excel_to_rdf(Path(__file__).parent / "043_exhaustive.xlsx", output_format="graph")
    assert compare.isomorphic(g1, g2), "Graphs are not Isomorphic"


def test_rdf_to_excel():
    tests_dir_path = Path(__file__).parent
    g1 = Graph().parse(tests_dir_path / "043_exhaustive.ttl")
    convert.rdf_to_excel(
        tests_dir_path / "043_exhaustive.ttl",
        output_file_path=tests_dir_path / "043_exhaustive_roundtrip.xlsx",
    )
    g2 = convert.excel_to_rdf(
        tests_dir_path / "043_exhaustive.xlsx",
        output_format="graph"
    )

    # clean up files
    Path(tests_dir_path / "043_exhaustive_roundtrip.xlsx").unlink(missing_ok=True)
    assert compare.isomorphic(g1, g2), "Graphs are not Isomorphic"
