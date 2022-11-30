import logging

from typing import Tuple, List

from openpyxl.worksheet.worksheet import Worksheet
from pydantic import ValidationError

from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import DCTERMS, OWL, PROV, RDF, RDFS, SDO, SKOS, XSD
import re
try:
    import models
    from utils import split_and_tidy_to_strings, ConversionError, load_workbook, string_is_http_iri, expand_namespaces, string_from_iri, id_from_iri, make_agent, split_and_tidy_to_iris, bind_namespaces
except:
    import sys

    sys.path.append("..")
    from vocexcel import models
    from vocexcel.utils import split_and_tidy_to_strings, ConversionError, load_workbook, string_is_http_iri, expand_namespaces, string_from_iri, id_from_iri, make_agent, split_and_tidy_to_iris, bind_namespaces


def extract_prefixes(sheet: Worksheet) -> dict[str, Namespace]:
    prefixes = {}
    for i in range(3, 100):
        pre = sheet[f"A{i}"].value
        if pre is None:
            break
        else:
            proper_pre = str(pre) if str(pre).endswith(":") else str(pre) + ":"
            prefixes[proper_pre] = sheet[f"B{i}"].value

    return prefixes


def extract_concept_scheme(sheet: Worksheet, prefixes) -> Graph:
    iri_s = sheet["B2"].value
    title = sheet["B3"].value
    description = sheet["B4"].value
    created = sheet["B5"].value
    modified = sheet["B6"].value
    creator = sheet["B7"].value
    publisher = sheet["B8"].value
    version = sheet["B9"].value
    provenance = sheet["B10"].value
    custodian = sheet["B11"].value

    if iri_s is None:
        raise ConversionError("Your vocabulary has no IRI. Please add it to the Concept Scheme sheet")
    else:
        iri = expand_namespaces(iri_s, prefixes)
        iri_conv = string_is_http_iri(str(iri))
        if not iri_conv[0]:
            raise ConversionError(iri_conv[1])

    if title is None:
        raise ConversionError("Your vocabulary has no title. Please add it to the Concept Scheme sheet")

    if description is None:
        raise ConversionError("Your vocabulary has no description. Please add it to the Concept Scheme sheet")

    if created is None:
        raise ConversionError("Your vocabulary has no created date. Please add it to the Concept Scheme sheet")

    if modified is None:
        raise ConversionError("Your vocabulary has no modified date. Please add it to the Concept Scheme sheet")

    if creator is None:
        raise ConversionError("Your vocabulary has no creator. Please add it to the Concept Scheme sheet")

    if publisher is None:
        raise ConversionError("Your vocabulary has no publisher. Please add it to the Concept Scheme sheet")

    if provenance is None:
        raise ConversionError("Your vocabulary has no provenance statement. Please add it to the Concept Scheme sheet")

    g = Graph(bind_namespaces="rdflib")
    g.add((iri, RDF.type, SKOS.ConceptScheme))
    g.add((iri, SKOS.prefLabel, Literal(title, lang="en")))
    g.add((iri, SKOS.definition, Literal(description, lang="en")))
    g.add((iri, DCTERMS.created, Literal(created.date(), datatype=XSD.date)))
    g.add((iri, DCTERMS.modified, Literal(modified.date(), datatype=XSD.date)))

    g += make_agent(creator, DCTERMS.creator, prefixes, iri)

    g += make_agent(publisher, DCTERMS.publisher, prefixes, iri)

    if version is not None:
        g.add((iri, OWL.versionInfo, Literal(str(version))))
        g.add((iri, OWL.versionIRI, URIRef(iri + "/" + str(version))))

    if custodian is not None:
        ISOROLES = Namespace("http://def.isotc211.org/iso19115/-1/2018/CitationAndResponsiblePartyInformation/code/CI_RoleCode/")
        g += make_agent(custodian, ISOROLES.custodian, prefixes, iri)
        g.bind("isoroles", ISOROLES)

    # auto-created
    g.add((iri, DCTERMS.identifier, id_from_iri(iri)))

    bind_namespaces(g, prefixes)
    return g


def extract_concepts(sheet: Worksheet, prefixes) -> Graph:
    g = Graph(bind_namespaces="rdflib")
    i = 4
    while True:
        # get values
        iri_s = sheet[f"A{i}"].value
        pref_label = sheet[f"B{i}"].value
        definition = sheet[f"C{i}"].value
        alt_labels = sheet[f"D{i}"].value
        narrower = sheet[f"E{i}"].value
        provenance = sheet[f"F{i}"].value
        source = sheet[f"G{i}"].value
        home = sheet[f"H{i}"].value

        # check values
        if iri_s is None:
            break

        iri = expand_namespaces(iri_s, prefixes)
        iri_conv = string_is_http_iri(str(iri))
        if not iri_conv[0]:
            raise ConversionError(iri_conv[1])

        if pref_label is None:
            raise ConversionError(f"You must provide a Preferred Label for Concept {iri_s}")

        if definition is None:
            raise ConversionError(f"You must provide a Definition for Concept {iri_s}")

        i += 1

        # ignore example Concepts
        if iri_s in ["http://example.com/earth-science", "http://example.com/atmospheric-science", "http://example.com/geology"]:
            continue

        # create Graph
        g.add((iri, RDF.type, SKOS.Concept))
        g.add((iri, SKOS.prefLabel, Literal(pref_label.strip(), lang="en")))
        g.add((iri, SKOS.definition, Literal(definition.strip(), lang="en")))

        if alt_labels is not None:
            for al in split_and_tidy_to_strings(alt_labels):
                g.add((iri, SKOS.altLabel, Literal(al, lang="en")))

        if narrower is not None:
            for n in split_and_tidy_to_iris(narrower, prefixes):
                g.add((iri, SKOS.narrower, n))

        if provenance is not None:
            g.add((iri, DCTERMS.provenance, Literal(provenance.strip())))

        if source is not None:
            g.add((iri, DCTERMS.source, Literal(source.strip(), datatype=XSD.anyURI)))

        if home is not None:
            g.add((iri, RDFS.isDefinedBy, URIRef(home.strip())))

    bind_namespaces(g, prefixes)
    return g


def extract_collections(sheet: Worksheet, prefixes) -> Graph:
    g = Graph(bind_namespaces="rdflib")
    i = 4
    while True:
        # get values
        iri_s = sheet[f"A{i}"].value
        pref_label = sheet[f"B{i}"].value
        definition = sheet[f"C{i}"].value
        members = sheet[f"D{i}"].value
        provenance = sheet[f"E{i}"].value

        # check values
        if iri_s is None:
            break

        iri = expand_namespaces(iri_s, prefixes)
        iri_conv = string_is_http_iri(str(iri))
        if not iri_conv[0]:
            raise ConversionError(iri_conv[1])

        if pref_label is None:
            raise ConversionError(f"You must provide a Preferred Label for Collection {iri_s}")

        if definition is None:
            raise ConversionError(f"You must provide a Definition for Collection {iri_s}")

        i += 1

        # create Graph
        g.add((iri, RDF.type, SKOS.Concept))
        g.add((iri, SKOS.prefLabel, Literal(pref_label, lang="en")))
        g.add((iri, SKOS.definition, Literal(definition, lang="en")))

        if members is not None:
            for n in split_and_tidy_to_iris(members, prefixes):
                g.add((iri, SKOS.member, n))

        if provenance is not None:
            g.add((iri, DCTERMS.provenance, Literal(provenance.strip())))

    bind_namespaces(g, prefixes)
    return g


def extract_additions_concept_properties(sheet: Worksheet) -> Graph:
    pass


def extract_and_apply_prefixes(sheet: Worksheet, g: Graph) -> None:
    pass
