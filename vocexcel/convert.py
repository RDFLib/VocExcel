import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, Literal, Union, Optional

import pyshacl
from colorama import Fore, Style
from pydantic.error_wrappers import ValidationError
from pyshacl.pytypes import GraphLike

try:
    import models
    import profiles
    from convert_021 import (
        extract_concepts_and_collections as extract_concepts_and_collections_021,
    )
    from convert_030 import (
        extract_concepts_and_collections as extract_concepts_and_collections_030,
        extract_concept_scheme as extract_concept_scheme_030,
    )
    from convert_040 import (
        extract_concepts_and_collections as extract_concepts_and_collections_040,
        extract_concept_scheme as extract_concept_scheme_040,
    )
    from convert_043 import (
        extract_concepts_and_collections as extract_concepts_and_collections_043,
        create_prefix_dict,
        extract_concept_scheme as extract_concept_scheme_043,
    )
    from utils import (
        ConversionError,
        load_workbook,
        get_template_version,
        KNOWN_FILE_ENDINGS,
        RDF_FILE_ENDINGS,
        KNOWN_TEMPLATE_VERSIONS,
        EXCEL_FILE_ENDINGS,
    )
except ImportError:
    sys.path.append("..")
    from vocexcel import models, profiles

    from vocexcel.convert_021 import (
        extract_concepts_and_collections as extract_concepts_and_collections_021,
    )
    from vocexcel.convert_030 import (
        extract_concepts_and_collections as extract_concepts_and_collections_030,
        extract_concept_scheme as extract_concept_scheme_030,
    )
    from vocexcel.convert_040 import (
        extract_concepts_and_collections as extract_concepts_and_collections_040,
        extract_concept_scheme as extract_concept_scheme_040,
    )
    from vocexcel.convert_043 import (
        extract_concepts_and_collections as extract_concepts_and_collections_043,
        create_prefix_dict,
        extract_concept_scheme as extract_concept_scheme_043,
    )
    from vocexcel.utils import (
        ConversionError,
        load_workbook,
        load_template,
        get_template_version,
        KNOWN_FILE_ENDINGS,
        RDF_FILE_ENDINGS,
        KNOWN_TEMPLATE_VERSIONS,
        EXCEL_FILE_ENDINGS,
    )

TEMPLATE_VERSION = None


def validate_with_profile(
    data_graph: Union[GraphLike, str, bytes],
    profile="vocpub",
    error_level=1,
    message_level=1,
    log_file=None,
):
    if profile not in profiles.PROFILES.keys():
        raise ValueError(
            "The profile chosen for conversion must be one of '{}'. 'vocpub' is default".format(
                "', '".join(profiles.PROFILES.keys())
            )
        )
    allow_warnings = True if error_level > 1 else False

    # validate the RDF file
    conforms, results_graph, results_text = pyshacl.validate(
        data_graph,
        shacl_graph=str(Path(__file__).parent / "validator.vocpub.ttl"),
        allow_warnings=allow_warnings,
    )

    logging_level = logging.INFO

    if message_level == 3:
        logging_level = logging.ERROR
    elif message_level == 2:
        logging_level = logging.WARNING

    if log_file:
        logging.basicConfig(
            level=logging_level, format="%(message)s", filename=log_file, force=True
        )
    else:
        logging.basicConfig(level=logging_level, format="%(message)s")

    info_list = []
    warning_list = []
    violation_list = []

    from rdflib.namespace import RDF, SH

    for report in results_graph.subjects(RDF.type, SH.ValidationReport):
        for result in results_graph.objects(report, SH.result):
            result_dict = {}
            for p, o in results_graph.predicate_objects(result):
                if p == SH.focusNode:
                    result_dict["focusNode"] = str(o)
                elif p == SH.resultMessage:
                    result_dict["resultMessage"] = str(o)
                elif p == SH.resultSeverity:
                    result_dict["resultSeverity"] = str(o)
                elif p == SH.sourceConstraintComponent:
                    result_dict["sourceConstraintComponent"] = str(o)
                elif p == SH.sourceShape:
                    result_dict["sourceShape"] = str(o)
                elif p == SH.value:
                    result_dict["value"] = str(o)
            result_message_formatted = log_msg(result_dict, log_file)
            result_message = log_msg(result_dict, "placeholder")
            if result_dict["resultSeverity"] == str(SH.Info):
                logging.info(result_message_formatted)
                info_list.append(result_message)
            elif result_dict["resultSeverity"] == str(SH.Warning):
                logging.warning(result_message_formatted)
                warning_list.append(result_message)
            elif result_dict["resultSeverity"] == str(SH.Violation):
                logging.error(result_message_formatted)
                violation_list.append(result_message)

    error_messages = []

    if error_level == 3:
        error_messages = violation_list
    elif error_level == 2:
        error_messages = warning_list + violation_list
    else:  # error_level == 1
        error_messages = info_list + warning_list + violation_list

    if len(error_messages) > 0:
        raise ConversionError(
            f"The file you supplied is not valid according to the {profile} profile."
        )


def excel_to_rdf(
    file_to_convert_path: Path,
    profile="vocpub",
    sheet_name: Optional[str] = None,
    output_file_path: Optional[Path] = None,
    output_format: Literal["turtle", "xml", "json-ld", "graph"] = "turtle",
    error_level=1,  # TODO: list Literal possible values
    message_level=1,  # TODO: list Literal possible values
    log_file: Optional[Path] = None,
    validate: Optional[bool] = False,
):
    """Converts a sheet within an Excel workbook to an RDF file"""
    wb = load_workbook(file_to_convert_path)
    template_version = get_template_version(wb)

    # test that we have a valid template variable.
    if template_version not in KNOWN_TEMPLATE_VERSIONS:
        raise ValueError(
            f"Unknown Template Version. Known Template Versions are {', '.join(KNOWN_TEMPLATE_VERSIONS)},"
            f" you supplied {template_version}"
        )

    # The way the voc is made - which Excel sheets to use - is dependent on the particular template version
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
    elif template_version == "0.4.3":
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
    profile: Optional[str] = "vocpub",
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
    from rdflib.namespace import DCAT, DCTERMS, PROV, RDF, RDFS, SKOS, OWL

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


def log_msg(result: Dict, log_file: str) -> str:
    from rdflib.namespace import SH

    formatted_msg = ""
    message = f"""Validation Result in {result['sourceConstraintComponent'].split(str(SH))[1]} ({result['sourceConstraintComponent']}):
\tSeverity: sh:{result['resultSeverity'].split(str(SH))[1]}
\tSource Shape: <{result['sourceShape']}>
\tFocus Node: <{result['focusNode']}>
\tValue Node: <{result.get('value', '')}>
\tMessage: {result['resultMessage']}
"""
    if result["resultSeverity"] == str(SH.Info):
        formatted_msg = (
            f"INFO: {message}"
            if log_file
            else Fore.BLUE + "INFO: " + Style.RESET_ALL + message
        )
    elif result["resultSeverity"] == str(SH.Warning):
        formatted_msg = (
            f"WARNING: {message}"
            if log_file
            else Fore.YELLOW + "WARNING: " + Style.RESET_ALL + message
        )
    elif result["resultSeverity"] == str(SH.Violation):
        formatted_msg = (
            f"VIOLATION: {message}"
            if log_file
            else Fore.RED + "VIOLATION: " + Style.RESET_ALL + message
        )
    return formatted_msg


def main(args=None):

    if args is None:  # vocexcel run via entrypoint
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="vocexcel", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-i",
        "--info",
        help="The version and other info of this instance of VocExcel.",
        action="store_true",
    )

    parser.add_argument(
        "-l",
        "--listprofiles",
        help="This flag, if set, must be the only flag supplied. It will cause the program to list all the vocabulary"
        " profiles that this converter, indicating both their URI and their short token for use with the"
        " -p (--profile) flag when converting Excel files",
        action="store_true",
    )

    parser.add_argument(
        "file_to_convert",
        nargs="?",  # allow 0 or 1 file name as argument
        type=Path,
        help="The Excel file to convert to a SKOS vocabulary in RDF or an RDF file to convert to an Excel file",
    )

    parser.add_argument(
        "-v", "--validate", help="Validate output file", action="store_true"
    )

    parser.add_argument(
        "-p",
        "--profile",
        help="A profile - a specified information model - for a vocabulary. This tool understands several profiles and"
        "you can choose which one you want to convert the Excel file according to. The list of profiles - URIs "
        "and their corresponding tokens - supported by VocExcel, can be found by running the program with the "
        "flag -lp or --listprofiles.",
        default="vocpub",
    )

    parser.add_argument(
        "-o",
        "--outputfile",
        help="An optionally-provided output file path. If not provided, output is to standard out.",
        required=False,
    )

    parser.add_argument(
        "-f",
        "--outputformat",
        help="An optionally-provided output format for RDF outputs. 'graph' returns the in-memory graph object, "
             "not serialized RDF.",
        required=False,
        choices=["turtle", "xml", "json-ld", "graph"],
        default="turtle",
    )

    parser.add_argument(
        "-s",
        "--sheet",
        help="The sheet within the target Excel Workbook to process",
        default="vocabulary",
    )

    parser.add_argument(
        "-t",
        "--templatefile",
        help="An optionally-provided Excel-template file to be used in SKOS-> Excel converion.",
        type=Path,
        required=False,
    )

    # 1 - info, 2 - warning, 3 - violation
    # error severity level
    parser.add_argument(
        "-e",
        "--errorlevel",
        help="The minimum severity level which fails validation",
        default=1,
    )

    # print severity level
    parser.add_argument(
        "-m",
        "--messagelevel",
        help="The minimum severity level printed to console",
        default=1,
    )

    # log to file
    parser.add_argument(
        "-g",
        "--logfile",
        help="The file to write logging output to",
        type=Path,
        required=False,
    )

    args = parser.parse_args(args)

    if not args:
        # show help if no args are given
        parser.print_help()
        parser.exit()

    if args.listprofiles:
        s = "Profiles\nToken\tIRI\n-----\t-----\n"
        for k, v in profiles.PROFILES.items():
            s += f"{k}\t{v.uri}\n"
        print(s.rstrip())
    elif args.info:
        # not sure what to do here, just removing the errors
        from vocexcel import __version__
        print(f"VocExel version: {__version__}")
        from vocexcel.utils import KNOWN_TEMPLATE_VERSIONS
        print(f"Known template versions: {', '.join(sorted(KNOWN_TEMPLATE_VERSIONS, reverse=True))}")
    elif args.file_to_convert:
        if not args.file_to_convert.suffix.lower().endswith(tuple(KNOWN_FILE_ENDINGS)):
            print(
                "Files for conversion must either end with .xlsx (Excel) or one of the known RDF file endings, '{}'".format(
                    "', '".join(RDF_FILE_ENDINGS.keys())
                )
            )
            parser.exit()

        print(f"Processing file {args.file_to_convert}")

        # input file looks like an Excel file, so convert Excel -> RDF
        if args.file_to_convert.suffix.lower().endswith(tuple(EXCEL_FILE_ENDINGS)):
            try:
                o = excel_to_rdf(
                    args.file_to_convert,
                    profile=args.profile,
                    sheet_name=args.sheet,
                    output_file_path=args.outputfile,
                    output_format=args.outputformat,
                    error_level=int(args.errorlevel),
                    message_level=int(args.messagelevel),
                    log_file=args.logfile,
                    validate=True,
                )
                if args.outputfile is None:
                    print(o)
            except ConversionError as err:
                logging.error("{0}".format(err))
                return 1

        # RDF file ending, so convert RDF -> Excel
        else:
            try:
                o = rdf_to_excel(
                    args.file_to_convert,
                    profile=args.profile,
                    output_file_path=args.outputfile,
                    template_file_path=args.templatefile,
                    error_level=int(args.errorlevel),
                    message_level=int(args.messagelevel),
                    log_file=args.logfile,
                )
                if args.outputfile is None:
                    print(o)
            except ConversionError as err:
                logging.error(f"{err}")
                return 1


if __name__ == "__main__":
    retval = main(sys.argv[1:])
    if retval is not None:
        sys.exit(retval)
