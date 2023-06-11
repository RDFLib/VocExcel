from pathlib import Path
from typing import Literal as TypeLiteral
from typing import Optional

from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS, XSD

try:
    import models
    from utils import (
        split_and_tidy_to_strings,
        ConversionError,
        load_workbook,
        string_is_http_iri,
        expand_namespaces,
        string_from_iri,
        id_from_iri,
        make_agent,
        split_and_tidy_to_iris,
        bind_namespaces,
        make_iri,
        validate_with_profile,
    )
except ImportError:
    import sys

    sys.path.append("..")
    from vocexcel import models
    from vocexcel.utils import (
        split_and_tidy_to_strings,
        ConversionError,
        load_workbook,
        string_is_http_iri,
        expand_namespaces,
        string_from_iri,
        id_from_iri,
        make_agent,
        split_and_tidy_to_iris,
        bind_namespaces,
        make_iri,
        validate_with_profile,
    )


def extract_prefixes(sheet: Worksheet) -> dict[str, Namespace]:
    prefixes = {}
    i = 3
    while True:
        pre = sheet[f"A{i}"].value
        if pre is None:
            break
        else:
            proper_pre = str(pre) if str(pre).endswith(":") else str(pre) + ":"
            prefixes[proper_pre] = sheet[f"B{i}"].value

        i += 1

    return prefixes


def extract_concept_scheme(sheet: Worksheet, prefixes) -> Graph:
    iri_s = sheet["B3"].value
    title = sheet["B4"].value
    description = sheet["B5"].value
    created = sheet["B6"].value
    modified = sheet["B7"].value
    creator = sheet["B8"].value
    publisher = sheet["B9"].value
    version = sheet["B10"].value
    history_note = sheet["B11"].value
    custodian = sheet["B12"].value

    if iri_s is None:
        raise ConversionError(
            "Your vocabulary has no IRI. Please add it to the Concept Scheme sheet"
        )
    else:
        iri = make_iri(iri_s, prefixes)

    if title is None:
        raise ConversionError(
            "Your vocabulary has no title. Please add it to the Concept Scheme sheet"
        )

    if description is None:
        raise ConversionError(
            "Your vocabulary has no description. Please add it to the Concept Scheme sheet"
        )

    if created is None:
        raise ConversionError(
            "Your vocabulary has no created date. Please add it to the Concept Scheme sheet"
        )

    if modified is None:
        raise ConversionError(
            "Your vocabulary has no modified date. Please add it to the Concept Scheme sheet"
        )

    if creator is None:
        raise ConversionError(
            "Your vocabulary has no creator. Please add it to the Concept Scheme sheet"
        )

    if publisher is None:
        raise ConversionError(
            "Your vocabulary has no publisher. Please add it to the Concept Scheme sheet"
        )

    if history_note is None:
        raise ConversionError(
            "Your vocabulary has no History Note statement. Please add it to the Concept Scheme sheet"
        )

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
        ISOROLES = Namespace(
            "http://def.isotc211.org/iso19115/-1/2018/CitationAndResponsiblePartyInformation/code/CI_RoleCode/"
        )
        g += make_agent(custodian, ISOROLES.custodian, prefixes, iri)
        g.bind("isoroles", ISOROLES)

    # auto-created
    g.add((iri, DCTERMS.identifier, id_from_iri(iri)))

    bind_namespaces(g, prefixes)
    return g, iri


def extract_concepts(sheet: Worksheet, prefixes, cs_iri) -> Graph:
    g = Graph(bind_namespaces="rdflib")
    i = 4
    while True:
        # get values
        iri_s = sheet[f"A{i}"].value
        pref_label = sheet[f"B{i}"].value
        definition = sheet[f"C{i}"].value
        alt_labels = sheet[f"D{i}"].value
        narrower = sheet[f"E{i}"].value
        history_note = sheet[f"F{i}"].value
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
            raise ConversionError(
                f"You must provide a Preferred Label for Concept {iri_s}"
            )

        if definition is None:
            raise ConversionError(f"You must provide a Definition for Concept {iri_s}")

        i += 1

        # ignore example Concepts
        if iri_s in [
            "http://example.com/earth-science",
            "http://example.com/atmospheric-science",
            "http://example.com/geology",
        ]:
            continue

        # create Graph
        g.add((iri, RDF.type, SKOS.Concept))
        g.add((iri, SKOS.inScheme, cs_iri))
        g.add((iri, SKOS.prefLabel, Literal(pref_label.strip(), lang="en")))
        g.add((iri, SKOS.definition, Literal(definition.strip(), lang="en")))

        if alt_labels is not None:
            for al in split_and_tidy_to_strings(alt_labels):
                g.add((iri, SKOS.altLabel, Literal(al, lang="en")))

        if narrower is not None:
            for n in split_and_tidy_to_iris(narrower, prefixes):
                g.add((iri, SKOS.narrower, n))

        if history_note is not None:
            g.add((iri, SKOS.historyNote, Literal(history_note.strip())))

        if source is not None:
            g.add((iri, DCTERMS.source, Literal(source.strip(), datatype=XSD.anyURI)))

        if home is not None:
            g.add((iri, RDFS.isDefinedBy, URIRef(home.strip())))

    bind_namespaces(g, prefixes)
    return g


def extract_collections(sheet: Worksheet, prefixes, cs_iri) -> Graph:
    g = Graph(bind_namespaces="rdflib")
    i = 4
    while True:
        # get values
        iri_s = sheet[f"A{i}"].value
        pref_label = sheet[f"B{i}"].value
        definition = sheet[f"C{i}"].value
        members = sheet[f"D{i}"].value
        history_note = sheet[f"E{i}"].value

        # check values
        if iri_s is None:
            break

        iri = expand_namespaces(iri_s, prefixes)
        iri_conv = string_is_http_iri(str(iri))
        if not iri_conv[0]:
            raise ConversionError(iri_conv[1])

        if pref_label is None:
            raise ConversionError(
                f"You must provide a Preferred Label for Collection {iri_s}"
            )

        if definition is None:
            raise ConversionError(
                f"You must provide a Definition for Collection {iri_s}"
            )

        # create Graph
        g.add((iri, RDF.type, SKOS.Collection))
        g.add((iri, SKOS.inScheme, cs_iri))
        g.add((iri, SKOS.prefLabel, Literal(pref_label, lang="en")))
        g.add((iri, SKOS.definition, Literal(definition, lang="en")))

        if members is not None:
            for n in split_and_tidy_to_iris(members, prefixes):
                g.add((iri, SKOS.member, n))

        if history_note is not None:
            g.add((iri, SKOS.historyNote, Literal(history_note.strip())))

        i += 1

    bind_namespaces(g, prefixes)
    return g


def extract_additions_concept_properties(sheet: Worksheet, prefixes) -> Graph:
    g = Graph(bind_namespaces="rdflib")
    i = 4
    while True:
        # get values
        iri_s = sheet[f"A{i}"].value
        related_s = sheet[f"B{i}"].value
        close_s = sheet[f"C{i}"].value
        exact_s = sheet[f"D{i}"].value
        narrow_s = sheet[f"E{i}"].value
        broad_s = sheet[f"F{i}"].value
        notation_s = sheet[f"G{i}"].value
        notation_type_s = sheet[f"H{i}"].value

        # check values
        if iri_s is None:
            break

        i += 1

        # ignore example Concepts
        if iri_s in [
            "http://example.com/geology",
        ]:
            continue

        # create Graph
        iri = make_iri(iri_s, prefixes)
        if related_s is not None:
            related = make_iri(related_s, prefixes)
            g.add((iri, SKOS.relatedMatch, related))

        if close_s is not None:
            close = make_iri(close_s, prefixes)
            g.add((iri, SKOS.closeMatch, close))

        if exact_s is not None:
            exact = make_iri(exact_s, prefixes)
            g.add((iri, SKOS.exactMatch, exact))

        if narrow_s is not None:
            narrow = make_iri(narrow_s, prefixes)
            g.add((iri, SKOS.narrowMatch, narrow))

        if broad_s is not None:
            broad = make_iri(broad_s, prefixes)
            g.add((iri, SKOS.broadMatch, broad))

        if notation_s is not None:
            if notation_type_s is not None:
                notation_type = make_iri(notation_type_s, prefixes)
            else:
                notation_type = XSD.token
            g.add(
                (
                    iri,
                    SKOS.notation,
                    Literal(notation_s, datatype=notation_type),
                )
            )

    bind_namespaces(g, prefixes)
    return g


def excel_to_rdf(
    wb: Workbook,
    output_file_path: Optional[Path] = None,
    output_format: TypeLiteral[
        "longturtle", "turtle", "xml", "json-ld", "graph"
    ] = "longturtle",
    validate: bool = False,
    profile="vocpub",
    error_level=1,
    message_level=1,
    log_file: Optional[Path] = None,
):
    prefixes = extract_prefixes(wb["Prefixes"])
    cs, cs_iri = extract_concept_scheme(wb["Concept Scheme"], prefixes)
    cons = extract_concepts(wb["Concepts"], prefixes, cs_iri)
    cols = extract_collections(wb["Collections"], prefixes, cs_iri)
    extra = extract_additions_concept_properties(
        wb["Additional Concept Properties"], prefixes
    )

    g = cs + cons + cols + extra

    if validate:
        validate_with_profile(
            g,
            profile=profile,
            error_level=error_level,
            message_level=message_level,
            log_file=log_file,
        )

    if output_file_path is not None:
        g.serialize(destination=str(output_file_path), format=output_format)
    else:  # print to std out
        if output_format == "graph":
            return g
        else:
            return g.serialize(format=output_format)
