import re
from pathlib import Path
from typing import Tuple, Optional
from openpyxl import load_workbook as _load_workbook
from openpyxl.workbook.workbook import Workbook
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, DCTERMS, PROV, XSD, DCAT, SKOS


EXCEL_FILE_ENDINGS = ["xlsx"]
RDF_FILE_ENDINGS = {
    ".ttl": "ttl",
    ".rdf": "xml",
    ".xml": "xml",
    ".json-ld": "json-ld",
    ".json": "json-ld",
    ".nt": "nt",
    ".n3": "n3",
}
KNOWN_FILE_ENDINGS = [str(x) for x in RDF_FILE_ENDINGS.keys()] + EXCEL_FILE_ENDINGS
KNOWN_TEMPLATE_VERSIONS = ["0.2.1", "0.3.0", "0.4.0", "0.4.1", "0.4.2", "0.4.3", "0.5.0"]
LATEST_TEMPLATE = KNOWN_TEMPLATE_VERSIONS[-1]


class ConversionError(Exception):
    pass


def load_workbook(file_path: Path) -> Workbook:
    if not file_path.name.lower().endswith(tuple(EXCEL_FILE_ENDINGS)):
        raise ValueError("Files for conversion to RDF must be Excel files ending .xlsx")
    return _load_workbook(filename=str(file_path), data_only=True)


def load_template(file_path: Path) -> Workbook:
    if not file_path.name.lower().endswith(tuple(EXCEL_FILE_ENDINGS)):
        raise ValueError(
            "Template files for RDF-to-Excel conversion must be Excel files ending .xlsx"
        )
    if get_template_version(load_workbook(file_path)) != LATEST_TEMPLATE:
        raise ValueError(
            f"Template files for RDF-to-Excel conversion must be of latest version ({LATEST_TEMPLATE})"
        )
    return _load_workbook(filename=str(file_path), data_only=True)


def get_template_version(wb: Workbook) -> str:
    # try 0.4.0 & 0.5.0 locations
    try:
        intro_sheet = wb["Introduction"]
        if intro_sheet["E11"].value in KNOWN_TEMPLATE_VERSIONS:
            return intro_sheet["E11"].value
        if intro_sheet["J11"].value in KNOWN_TEMPLATE_VERSIONS:
            return intro_sheet["J11"].value
    except Exception:
        pass

    # try 0.2.1 & 0.3.0 locations
    try:
        # older template version
        pi = wb["program info"]
        if pi["B2"].value in KNOWN_TEMPLATE_VERSIONS:
            return pi["B2"].value
    except Exception:
        pass

    # if we get here, the template version is either unknown or can't be located
    raise Exception(
        "The version of the Excel template you are using cannot be determined"
    )


def split_and_tidy_to_strings(s: str):
    # note this may not work in list of things that contain commas. Need to consider revising
    # to allow comma-seperated values where it'll split in commas but not in things enclosed in quotes.
    if s == "" or s is None:
        return []
    else:
        return [x.strip() for x in re.split(r",\n", s.strip())]


def split_and_tidy_to_iris(s: str, prefixes):
    return [expand_namespaces(ss.strip(), prefixes) for ss in split_and_tidy_to_strings(s)]


def string_is_http_iri(s: str) -> Tuple[bool, str]:
    # returns (True, None) if the string (sort of) is an IRI
    # returns (False, message) otherwise
    messages = []
    if not s.startswith("http"):
        messages.append(f"HTTP IRIs must start with 'http' or 'https'. Your value was '{s}'")
        if ":" in s:
            messages.append(
                f"It looks like your IRI might contain a prefix, {s.split(':')[0]+':'}, that could not be expanded. "
                "Check it's present in the Prefixes sheet of your workbook")

    if " " in s:
        messages.append("IRIs cannot contain spaces")

    if len(messages) > 0:
        return False, " and ".join(messages)
    else:
        return True, ""


def all_strings_in_list_are_iris(l_: []) -> Tuple[bool, str]:
    messages = []
    if l_ is not None:
        for item in l_:
            r = string_is_http_iri(item)
            if not r[0]:
                messages.append(f"Item {item} failed with messages {r[1]}")

    if len(messages) > 0:
        return False, " and ".join(messages)
    else:
        return True, ""


def expand_namespaces(s: str, prefixes: dict[str, Namespace]) -> URIRef:
    for pre in prefixes.keys():
        if s.startswith(pre):
            return URIRef(s.replace(pre, prefixes[pre]))
    return URIRef(s)


def bind_namespaces(g: Graph, prefixes: dict[str, Namespace]):
    for pre, ns in prefixes.items():
        g.bind(pre.rstrip(":"), ns)


def string_from_iri(iri):
    s = str(iri.split("/")[-1].split("#")[-1])
    s = re.sub(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", " ", s)
    s = s.title()
    s = s.replace("-", " ")

    return s


def id_from_iri(iri):
    id = str(iri.split("/")[-1].split("#")[-1])
    return Literal(id, datatype=XSD.token)


def make_agent(agent_value, agent_role, prefixes, iri_of_subject) -> Graph:
    ag = Graph()
    iri = expand_namespaces(agent_value, prefixes)
    creator_iri_conv = string_is_http_iri(str(iri))
    if not creator_iri_conv[0]:
        iri = BNode()
    ag.add((iri, RDF.type, PROV.Agent))
    ag.add((iri, RDFS.label, Literal(string_from_iri(agent_value))))
    if agent_role in [DCTERMS.creator, DCTERMS.publisher, DCTERMS.rightsHolder]:
        ag.add((iri_of_subject, agent_role, iri))
    else:
        qa = BNode()
        ag.add((iri_of_subject, PROV.qualifiedAttribution, qa))
        ag.add((qa, PROV.agent, iri))
        ag.add((qa, DCAT.hadRole, agent_role))

    return ag
