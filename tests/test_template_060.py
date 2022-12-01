import sys
from pathlib import Path

import pytest
from rdflib import Graph, URIRef, Literal, compare, Namespace
from rdflib.namespace import DCTERMS, SKOS, RDF
from textwrap import dedent

sys.path.append(str(Path(__file__).parent.parent.absolute()))
from vocexcel.utils import ConversionError, load_workbook, expand_namespaces
from vocexcel.convert_060 import (
    extract_prefixes,
    extract_concept_scheme,
    extract_concepts,
    extract_collections,
    extract_additions_concept_properties,
    excel_to_rdf,
)


def test_extract_prefixes():
    g = Graph()

    wb = load_workbook(Path(__file__).parent / "060_simple.xlsx")

    n = extract_prefixes(wb["Prefixes"])

    g.add(
        (
            expand_namespaces("ex:thing-1", n),
            SKOS.prefLabel,
            Literal("Thing 1", lang="en"),
        )
    )
    g.add(
        (
            expand_namespaces("ch:rhode-island-red", n),
            SKOS.prefLabel,
            Literal("Rhode Island Red", lang="en"),
        )
    )

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
    wb = load_workbook(Path(__file__).parent / "060_simple.xlsx")
    prefixes = extract_prefixes(wb["Prefixes"])
    cs = extract_concept_scheme(wb["Concept Scheme"], prefixes)

    # no IRI
    with pytest.raises(ConversionError) as e:
        wb = load_workbook(Path(__file__).parent / "060_simple2_i.xlsx")
        prefixes = extract_prefixes(wb["Prefixes"])
        extract_concept_scheme(wb["Concept Scheme"], prefixes)

    # IRI starts with unknown prefix
    with pytest.raises(ConversionError) as e:
        wb = load_workbook(Path(__file__).parent / "060_simple3_i.xlsx")
        prefixes = extract_prefixes(wb["Prefixes"])
        extract_concept_scheme(wb["Concept Scheme"], prefixes)


def test_extract_concepts():
    wb = load_workbook(Path(__file__).parent / "060_simple.xlsx")
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
    skos:altLabel
        "Chinese silk chicken"@en ,
        "Silky"@en ;
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


def test_extract_collections():
    wb = load_workbook(Path(__file__).parent / "060_simple.xlsx")
    prefixes = extract_prefixes(wb["Prefixes"])
    cols = extract_collections(wb["Collections"], prefixes)
    # print(cols.serialize(format="longturtle"))
    expected = """
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX ex: <http://example.com/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        
        ex:small-chickens
            a skos:Concept ;
            dcterms:provenance "Just made up" ;
            skos:definition "Breeds of small chickens"@en ;
            skos:member
                ex:bantam ,
                ex:silkie ;
            skos:prefLabel "Small Chickens"@en ;
        .    
        """
    g2 = Graph().parse(data=expected)
    # print((g2 - cols).serialize(format="longturtle"))
    # print("++++++++++++++")
    # print((cols - g2).serialize(format="longturtle"))
    # print(g2.serialize(format="longturtle"))
    assert compare.isomorphic(cols, g2)


def test_extract_additions_concept_properties():
    wb = load_workbook(Path(__file__).parent / "060_simple.xlsx")
    prefixes = extract_prefixes(wb["Prefixes"])
    extra = extract_additions_concept_properties(
        wb["Additional Concept Properties"], prefixes
    )
    expected = """
        PREFIX cdterms: <http://purl.org/dc/terms/>
        PREFIX ex: <http://example.com/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        
        ex:bantam
            cdterms:identifier "B"^^<http://system-x.com> ;
            skos:relatedMatch <http://other-voc.com/bantam> ;
        .
        """
    g2 = Graph().parse(data=expected)
    assert compare.isomorphic(extra, g2)


def test_rdf_to_excel():
    wb = load_workbook(Path(__file__).parent / "060_simple.xlsx")
    g = excel_to_rdf(wb, output_format="graph")
    # print(g.serialize(format="longturtle"))
    expected = """
        PREFIX cdterms: <http://purl.org/dc/terms/>
        PREFIX ch: <http://example.com/chickens/>
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX ex: <http://example.com/>
        PREFIX isoroles: <http://def.isotc211.org/iso19115/-1/2018/CitationAndResponsiblePartyInformation/code/CI_RoleCode/>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        
        ex:chickens
            a skos:ConceptScheme ;
            cdterms:created "2022-12-01"^^xsd:date ;
            cdterms:creator [
                    a prov:Agent ;
                    rdfs:label "Nicholas Car"
                ] ;
            cdterms:identifier "chickens"^^xsd:token ;
            cdterms:modified "2022-12-01"^^xsd:date ;
            cdterms:publisher <http://linked.data.gov.au/org/agldwg> ;
            owl:versionIRI ch:0.0.1 ;
            owl:versionInfo "0.0.1" ;
            skos:definition "A vocabulary of breeds of chicken"@en ;
            skos:prefLabel "Chickens Breeds"@en ;
            prov:qualifiedAttribution [
                    dcat:hadRole isoroles:custodian ;
                    prov:agent [
                            a prov:Agent ;
                            rdfs:label "Nicholas Car"
                        ]
                ] ;
        .
        
        ex:rhode-island-red
            a skos:Concept ;
            cdterms:provenance "Taken from Wikipedia" ;
            cdterms:source "https://en.wikipedia.org/wiki/Rhode_Island_Red"^^xsd:anyURI ;
            skos:definition "The Rhode Island Red is an American breed of domestic chicken. It is the state bird of Rhode Island."@en ;
            skos:prefLabel "Rhode Island Red"@en ;
        .
        
        ex:small-chickens
            a skos:Concept ;
            cdterms:provenance "Just made up" ;
            skos:definition "Breeds of small chickens"@en ;
            skos:member
                ex:bantam ,
                ex:silkie ;
            skos:prefLabel "Small Chickens"@en ;
        .
        
        ex:bantam
            a skos:Concept ;
            cdterms:identifier "B"^^<http://system-x.com> ;
            cdterms:source "https://en.wikipedia.org/wiki/Bantam_(poultry)"^^xsd:anyURI ;
            skos:definition "A bantam is any small variety of fowl, usually of chicken or duck."@en ;
            skos:narrower ex:silkie ;
            skos:prefLabel "Bantam"@en ;
            skos:relatedMatch <http://other-voc.com/bantam> ;
        .
        
        <http://linked.data.gov.au/org/agldwg>
            a prov:Agent ;
            rdfs:label "Agldwg" ;
        .
        
        ex:silkie
            a skos:Concept ;
            skos:altLabel
                "Chinese silk chicken"@en ,
                "Silky"@en ;
            skos:definition "The Silkie (also known as the Silky or Chinese silk chicken) is a breed of chicken named for its atypically fluffy plumage, which is said to feel like silk and satin."@en ;
            skos:prefLabel "Silkie"@en ;
        .    
    """
    g2 = Graph().parse(data=expected)
    assert compare.isomorphic(g, g2)
