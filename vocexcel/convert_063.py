from pathlib import Path
from typing import Literal as TypeLiteral
from typing import Optional

from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from rdflib import Graph, Literal, Namespace, URIRef, BNode
from rdflib.namespace import DCAT, DCTERMS, OWL, PROV, RDF, RDFS, SDO, SKOS, XSD
REG = Namespace("http://purl.org/linked-data/registry#")

try:
    import models
    from utils import (
        ConversionError,
        add_top_concepts,
        bind_namespaces,
        expand_namespaces,
        id_from_iri,
        load_workbook,
        make_agent,
        make_iri,
        split_and_tidy_to_iris,
        split_and_tidy_to_strings,
        string_from_iri,
        string_is_http_iri,
        validate_with_profile,
        STATUSES,
        VOCDERMODS,
    )
except ImportError:
    import sys

    sys.path.append("..")
    from vocexcel import models
    from vocexcel.utils import (
        ConversionError,
        add_top_concepts,
        bind_namespaces,
        expand_namespaces,
        id_from_iri,
        load_workbook,
        make_agent,
        make_iri,
        split_and_tidy_to_iris,
        split_and_tidy_to_strings,
        string_from_iri,
        string_is_http_iri,
        validate_with_profile,
        STATUSES,
        VOCDERMODS,
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


def extract_concept_scheme(sheet: Worksheet, prefixes, template_version="0.6.3") -> tuple[Graph, str]:
    iri_s = sheet["B3"].value
    title = sheet["B4"].value
    description = sheet["B5"].value
    created = sheet["B6"].value
    modified = sheet["B7"].value
    creator = sheet["B8"].value
    publisher = sheet["B9"].value
    if template_version == "0.6.2":
        custodian = sheet["B12"].value
        version = str(sheet["B10"].value).strip("'")
        history_note = sheet["B11"].value
        status = None
        derived_from = None
        voc_der_mod = None
        themes = None
    else:  # 0.6.3
        custodian = sheet["B10"].value
        version = str(sheet["B11"].value).strip("'")
        history_note = sheet["B12"].value
        status = sheet["B13"].value
        derived_from = sheet["B14"].value
        voc_der_mod = sheet["B15"].value
        themes = split_and_tidy_to_strings(sheet["B16"].value)

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

    if status is not None and status not in STATUSES:
        raise ConversionError(
            f"You have supplied a status for your vocab of {status} but it is not recognised. "
            f"If supplied, it must be one of {', '.join(STATUSES.keys())}"
        )

    if derived_from is not None:
        if voc_der_mod is None:
            raise ConversionError(
                "If you supply a 'Derived From' value - IRI of another vocab - "
                "you must also supply a 'Derivation Mode' value")

        if voc_der_mod not in VOCDERMODS:
            raise ConversionError(
                f"You have supplied a vocab derivation mode for your vocab of {voc_der_mod} but it is not recognised. "
                f"If supplied, it must be one of {', '.join(VOCDERMODS.keys())}"
            )

        derived_from = make_iri(derived_from, prefixes)

    g = Graph(bind_namespaces="rdflib")
    g.add((iri, RDF.type, SKOS.ConceptScheme))
    g.add((iri, SKOS.prefLabel, Literal(title, lang="en")))
    g.add((iri, SKOS.definition, Literal(description, lang="en")))
    g.add((iri, DCTERMS.created, Literal(created.date(), datatype=XSD.date)))
    g.add((iri, DCTERMS.modified, Literal(modified.date(), datatype=XSD.date)))
    g.add((iri, SKOS.historyNote, Literal(history_note, lang="en")))

    g += make_agent(creator, DCTERMS.creator, prefixes, iri)

    g += make_agent(publisher, DCTERMS.publisher, prefixes, iri)

    if custodian is not None:
        for _custodian in split_and_tidy_to_strings(custodian):
            ISOROLES = Namespace(
                "http://def.isotc211.org/iso19115/-1/2018/CitationAndResponsiblePartyInformation/code/CI_RoleCode/"
            )
            g += make_agent(_custodian, ISOROLES.custodian, prefixes, iri)
            g.bind("isoroles", ISOROLES)

    if version is not None:
        g.add((iri, OWL.versionInfo, Literal(str(version))))
        g.add((iri, OWL.versionIRI, URIRef(iri + "/" + str(version))))

    if status is not None:
        g.add((iri, REG.status, URIRef(STATUSES[status])))

    if derived_from is not None:
        qd = BNode()
        g.add((iri, PROV.qualifiedDerivation, qd))
        g.add((qd, PROV.entity, URIRef(derived_from)))
        g.add((qd, PROV.hadRole, URIRef(VOCDERMODS[voc_der_mod])))

    if themes is not None:
        for theme in themes:
            try:
                theme = make_iri(theme, prefixes)
            except ConversionError:
                theme = Literal(theme)
            g.add((iri, DCAT.theme, theme))

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
        if str(iri).startswith(str(cs_iri)):
            g.add((iri, RDFS.isDefinedBy, cs_iri))
        if "@" in pref_label:
            val, lang = pref_label.strip().split("@")
            g.add((iri, SKOS.prefLabel, Literal(val, lang=lang)))
        else:
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
            for _source in split_and_tidy_to_strings(source):
                g.add(
                    (iri, DCTERMS.source, Literal(_source.strip(), datatype=XSD.anyURI))
                )

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
        g.add((iri, RDFS.isDefinedBy, cs_iri))
        if str(iri).startswith(str(cs_iri)):
            g.add((iri, RDFS.isDefinedBy, cs_iri))
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
    profile="vocpub-43",
    error_level=1,
    message_level=1,
    log_file: Optional[Path] = None,
    template_version="0.6.3"
):
    prefixes = extract_prefixes(wb["Prefixes"])
    cs, cs_iri = extract_concept_scheme(wb["Concept Scheme"], prefixes, template_version)
    cons = extract_concepts(wb["Concepts"], prefixes, cs_iri)
    cols = extract_collections(wb["Collections"], prefixes, cs_iri)
    extra = extract_additions_concept_properties(
        wb["Additional Concept Properties"], prefixes
    )

    g = cs + cons + cols + extra
    g = add_top_concepts(g)
    g.bind("cs", cs_iri)
    g.bind("reg", REG)

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
