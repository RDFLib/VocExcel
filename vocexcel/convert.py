from pathlib import Path
from typing import BinaryIO, Literal, Optional

from pydantic.error_wrappers import ValidationError

from vocexcel import models
from vocexcel.convert_021 import (
    extract_concepts_and_collections as extract_concepts_and_collections_021,
)
from vocexcel.convert_030 import (
    extract_concept_scheme as extract_concept_scheme_030,
)
from vocexcel.convert_030 import (
    extract_concepts_and_collections as extract_concepts_and_collections_030,
)
from vocexcel.convert_040 import (
    extract_concept_scheme as extract_concept_scheme_040,
)
from vocexcel.convert_040 import (
    extract_concepts_and_collections as extract_concepts_and_collections_040,
)
from vocexcel.convert_043 import (
    create_prefix_dict,
)
from vocexcel.convert_043 import (
    extract_concept_scheme as extract_concept_scheme_043,
)
from vocexcel.convert_043 import (
    extract_concepts_and_collections as extract_concepts_and_collections_043,
)
from vocexcel.convert_060 import excel_to_rdf as excel_to_rdf_060
from vocexcel.convert_063 import excel_to_rdf as excel_to_rdf_063
from vocexcel.convert_070 import excel_to_rdf as excel_to_rdf_070
from vocexcel.utils import (
    RDF_FILE_ENDINGS,
    ConversionError,
    get_template_version,
    load_template,
    load_workbook,
    validate_with_profile,
)

TEMPLATE_VERSION = None


def excel_to_rdf(
    file_to_convert_path: Path | BinaryIO,
    profile="vocpub-46",
    sheet_name: Optional[str] = None,
    output_file_path: Optional[Path] = None,
    output_format: Literal["turtle", "xml", "json-ld", "graph"] = "longturtle",
    error_level=1,  # TODO: list Literal possible values
    message_level=1,  # TODO: list Literal possible values
    log_file: Optional[Path] = None,
    validate: Optional[bool] = False,
):
    """Converts a sheet within an Excel workbook to an RDF file"""
    wb = load_workbook(file_to_convert_path)
    template_version = get_template_version(wb)

    if template_version in ["0.7.0"]:
        return excel_to_rdf_070(
            wb,
            output_file_path,
            output_format,
            validate,
            profile,
            error_level,
            message_level,
            log_file,
            template_version
        )

    # The way the voc is made - which Excel sheets to use - is dependent on the particular template version
    elif template_version in ["0.6.2", "0.6.3"]:
        return excel_to_rdf_063(
            wb,
            output_file_path,
            output_format,
            validate,
            profile,
            error_level,
            message_level,
            log_file,
            template_version
        )

    elif template_version in ["0.5.0", "0.6.0", "0.6.1"]:
        return excel_to_rdf_060(
            wb,
            output_file_path,
            output_format,
            validate,
            profile,
            error_level,
            message_level,
            log_file,
        )

    elif template_version in ["0.4.3", "0.4.4"]:
        try:
            sheet = wb["Concept Scheme"]
            concept_sheet = wb["Concepts"]
            additional_concept_sheet = wb["Additional Concept Features"]
            collection_sheet = wb["Collections"]
            prefix_sheet = wb["Prefix Sheet"]
            prefix = create_prefix_dict(prefix_sheet)

            concepts, collections = extract_concepts_and_collections_043(
                concept_sheet, additional_concept_sheet, collection_sheet, prefix
            )
            cs = extract_concept_scheme_043(sheet, prefix)
        except ValidationError as e:
            raise ConversionError(f"ConceptScheme processing error: {e}")

    elif template_version == "0.3.0" or template_version == "0.2.1":
        sheet = wb["vocabulary" if sheet_name is None else sheet_name]
        # read from the vocabulary sheet of the workbook unless given a specific sheet

        if template_version == "0.2.1":
            concepts, collections = extract_concepts_and_collections_021(sheet)
        elif template_version == "0.3.0":
            concepts, collections = extract_concepts_and_collections_030(sheet)

        try:
            cs = extract_concept_scheme_030(sheet)
        except ValidationError as e:
            raise ConversionError(f"ConceptScheme processing error: {e}")

    elif (
        template_version == "0.4.0"
        or template_version == "0.4.1"
        or template_version == "0.4.2"
    ):
        try:
            sheet = wb["Concept Scheme"]
            concept_sheet = wb["Concepts"]
            additional_concept_sheet = wb["Additional Concept Features"]
            collection_sheet = wb["Collections"]

            concepts, collections = extract_concepts_and_collections_040(
                concept_sheet, additional_concept_sheet, collection_sheet
            )
            cs = extract_concept_scheme_040(sheet)
        except ValidationError as e:
            raise ConversionError(f"ConceptScheme processing error: {e}")

    # Build the total vocab
    vocab_graph = models.Vocabulary(
        concept_scheme=cs, concepts=concepts, collections=collections
    ).to_graph()

    if validate:
        validate_with_profile(
            vocab_graph,
            profile=profile,
            error_level=error_level,
            message_level=message_level,
            log_file=log_file,
        )

    if output_file_path is not None:
        vocab_graph.serialize(destination=str(output_file_path), format=output_format)
    else:  # print to std out
        if output_format == "graph":
            return vocab_graph
        else:
            return vocab_graph.serialize(format=output_format)


def rdf_to_excel(
    file_to_convert_path: Path,
    profile: Optional[str] = "vocpub-46",
    output_file_path: Optional[Path] = None,
    template_file_path: Optional[Path] = None,
    error_level=1,
    message_level=1,
    log_file=None,
):
    if type(file_to_convert_path) is str:
        file_to_convert_path = Path(file_to_convert_path)
    if not file_to_convert_path.name.endswith(tuple(RDF_FILE_ENDINGS.keys())):
        raise ValueError(
            "Files for conversion to Excel must end with one of the RDF file formats: '{}'".format(
                "', '".join(RDF_FILE_ENDINGS.keys())
            )
        )

    validate_with_profile(
        str(file_to_convert_path),
        profile=profile,
        error_level=error_level,
        message_level=message_level,
        log_file=log_file,
    )
    # the RDF is valid so extract data and create Excel
    from rdflib import Graph
    from rdflib.namespace import DCAT, DCTERMS, OWL, PROV, RDF, RDFS, SKOS

    g = Graph().parse(
        str(file_to_convert_path), format=RDF_FILE_ENDINGS[file_to_convert_path.suffix]
    )

    if template_file_path is None:
        wb = load_template(file_path=(Path(__file__).parent / "blank_043.xlsx"))
    else:
        wb = load_template(file_path=template_file_path)

    holder = {"hasTopConcept": [], "provenance": None}
    for s in g.subjects(RDF.type, SKOS.ConceptScheme):
        holder["uri"] = str(s)
        for p, o in g.predicate_objects(s):
            if p == SKOS.prefLabel:
                holder["title"] = o.toPython()
            elif p == SKOS.definition:
                holder["description"] = str(o)
            elif p == DCTERMS.created:
                holder["created"] = o.toPython()
            elif p == DCTERMS.modified:
                holder["modified"] = o.toPython()
            elif p == DCTERMS.creator:
                holder["creator"] = (
                    models.ORGANISATIONS_INVERSE[o]
                    if models.ORGANISATIONS_INVERSE.get(o)
                    else str(o)
                )
            elif p == DCTERMS.publisher:
                holder["publisher"] = (
                    models.ORGANISATIONS_INVERSE[o]
                    if models.ORGANISATIONS_INVERSE.get(o)
                    else str(o)
                )
            elif p == OWL.versionInfo:
                holder["versionInfo"] = str(o)
            elif p == DCTERMS.source:
                holder["provenance"] = str(o)
            elif p == DCTERMS.provenance:
                holder["provenance"] = str(o)
            elif p == PROV.wasDerivedFrom:
                holder["provenance"] = str(o)
            elif p == SKOS.hasTopConcept:
                holder["hasTopConcept"].append(str(o))
            elif p == DCAT.contactPoint:
                holder["custodian"] = str(o)
            elif p == RDFS.seeAlso:
                holder["pid"] = str(o)

    # from models import ConceptScheme, Concept, Collection
    cs = models.ConceptScheme(
        uri=holder["uri"],
        title=holder["title"],
        description=holder["description"],
        created=holder["created"],
        modified=holder["modified"],
        creator=holder["creator"],
        publisher=holder["publisher"],
        version=holder.get("versionInfo", None),
        provenance=holder.get("provenance", None),
        custodian=holder.get("custodian", None),
        pid=holder.get("pid", None),
    )
    cs.to_excel(wb)

    # infer inverses
    for s, o in g.subject_objects(SKOS.broader):
        g.add((o, SKOS.narrower, s))

    row_no_features, row_no_concepts = 3, 3
    for s in g.subjects(RDF.type, SKOS.Concept):
        holder = {
            "uri": str(s),
            "pref_label": [],
            "pl_language_code": [],
            "definition": [],
            "def_language_code": [],
            "children": [],
            "alt_labels": [],
            "home_vocab_uri": None,
            "provenance": None,
            "related_match": [],
            "close_match": [],
            "exact_match": [],
            "narrow_match": [],
            "broad_match": [],
        }
        for p, o in g.predicate_objects(s):
            if p == SKOS.prefLabel:
                holder["pref_label"].append(o.toPython())
                holder["pl_language_code"].append(o.language)
            elif p == SKOS.definition:
                holder["definition"].append(str(o))
                holder["def_language_code"].append(o.language)
            elif p == SKOS.narrower:
                holder["children"].append(str(o))
            elif p == SKOS.altLabel:
                holder["alt_labels"].append(str(o))
            elif p == RDFS.isDefinedBy:
                holder["home_vocab_uri"] = str(o)
            elif p == DCTERMS.source:
                holder["provenance"] = str(o)
            elif p == DCTERMS.provenance:
                holder["provenance"] = str(o)
            elif p == PROV.wasDerivedFrom:
                holder["provenance"] = str(o)
            elif p == SKOS.relatedMatch:
                holder["related_match"].append(str(o))
            elif p == SKOS.closeMatch:
                holder["close_match"].append(str(o))
            elif p == SKOS.exactMatch:
                holder["exact_match"].append(str(o))
            elif p == SKOS.narrowMatch:
                holder["narrow_match"].append(str(o))
            elif p == SKOS.broadMatch:
                holder["broad_match"].append(str(o))

        row_no_concepts = models.Concept(
            uri=holder["uri"],
            pref_label=holder["pref_label"],
            pl_language_code=holder["pl_language_code"],
            definition=holder["definition"],
            def_language_code=holder["def_language_code"],
            children=holder["children"],
            alt_labels=holder["alt_labels"],
            home_vocab_uri=holder["home_vocab_uri"],
            provenance=holder["provenance"],
            related_match=holder["related_match"],
            close_match=holder["close_match"],
            exact_match=holder["exact_match"],
            narrow_match=holder["narrow_match"],
            broad_match=holder["broad_match"],
        ).to_excel(wb, row_no_features, row_no_concepts)
        row_no_features += 1

    row_no = 3

    for s in g.subjects(RDF.type, SKOS.Collection):
        holder = {"uri": str(s), "members": []}
        for p, o in g.predicate_objects(s):
            if p == SKOS.prefLabel:
                holder["pref_label"] = o.toPython()
            elif p == SKOS.definition:
                holder["definition"] = str(o)
            elif p == SKOS.member:
                holder["members"].append(str(o))
            elif p == DCTERMS.source:
                holder["provenance"] = str(o)
            elif p == DCTERMS.provenance:
                holder["provenance"] = str(o)
            elif p == PROV.wasDerivedFrom:
                holder["provenance"] = str(o)

        models.Collection(
            uri=holder["uri"],
            pref_label=holder["pref_label"],
            definition=holder["definition"],
            members=holder["members"],
            provenance=holder["provenance"]
            if holder.get("provenance") is not None
            else None,
        ).to_excel(wb, row_no)
        row_no += 1

    if output_file_path is not None:
        dest = output_file_path
    else:
        dest = file_to_convert_path.with_suffix(".xlsx")
    wb.save(filename=dest)
    return dest

