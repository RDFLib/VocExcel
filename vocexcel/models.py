from typing import List
from pydantic import BaseModel, ValidationError, validator
from pydantic import AnyHttpUrl
import datetime
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import DCAT, DCTERMS, OWL, SKOS, RDF, RDFS, XSD


ORGANISATIONS = {
    "CGI": URIRef("https://linked.data.gov.au/org/cgi"),
    "GA": URIRef("https://linked.data.gov.au/org/ga"),
    "GGIC": URIRef("https://linked.data.gov.au/org/ggic"),
    "GSQ": URIRef("https://linked.data.gov.au/org/gsq"),
    "ICSM": URIRef("https://linked.data.gov.au/org/icsm"),
}


class ConceptScheme(BaseModel):
    uri: AnyHttpUrl
    title: str
    description: str
    created: datetime.date
    modified: datetime.date = None
    creator: str
    publisher: str
    version: str
    provenance: str
    custodian: str = None
    pid: AnyHttpUrl = None

    @validator("creator")
    def creator_must_be_from_list(cls, v):
        if v not in ORGANISATIONS.keys():
            raise ValueError(f"Organisations must selected from the Organisations list: {', '.join(ORGANISATIONS)}")
        return v

    @validator("publisher")
    def publisher_must_be_from_list(cls, v):
        if v not in ORGANISATIONS.keys():
            raise ValueError(f"Organisations must selected from the Organisations list: {', '.join(ORGANISATIONS)}")
        return v

    def to_graph(self):
        g = Graph()
        v = URIRef(self.uri)
        g.add((v, RDF.type, SKOS.ConceptScheme))
        g.add((v, SKOS.prefLabel, Literal(self.title, lang="en")))
        g.add((v, SKOS.definition, Literal(self.description, lang="en")))
        g.add((v, DCTERMS.created, Literal(self.created, datatype=XSD.date)))
        if self.modified is not None:
            g.add((v, DCTERMS.modified, Literal(self.created, datatype=XSD.date)))
        else:
            g.add((v, DCTERMS.modified, Literal(datetime.datetime.now().strftime("%Y-%m-%d"), datatype=XSD.date)))
        g.add((v, DCTERMS.creator, ORGANISATIONS[self.creator]))
        g.add((v, DCTERMS.publisher, ORGANISATIONS[self.publisher]))
        if self.version is not None:
            g.add((v, OWL.versionInfo, Literal(self.version)))
        g.add((v, DCTERMS.provenance, Literal(self.provenance, lang="en")))
        if self.custodian is not None:
            g.add((v, DCAT.contactPoint, Literal(self.custodian)))
        if self.pid is not None:
            g.add((v, RDFS.seeAlso, URIRef(self.pid)))

        # bind non-core prefixes
        g.bind("cs", v)
        g.bind("", str(v).split("#")[0] if "#" in str(v) else "/".join(str(v).split("/")[:-1]))
        g.bind("dcat", DCAT)
        g.bind("dcterms", DCTERMS)
        g.bind("skos", SKOS)
        g.bind("owl", OWL)

        return g


class Concept(BaseModel):
    uri: AnyHttpUrl
    pref_label: str
    alt_labels: List[str] = None
    definition: str
    children: List[AnyHttpUrl] = None
    other_ids: List[str] = None
    home_vocab_uri: AnyHttpUrl = None
    provenance: str = None

    def to_graph(self):
        g = Graph()
        c = URIRef(self.uri)
        g.add((c, RDF.type, SKOS.Concept))
        g.add((c, SKOS.prefLabel, Literal(self.pref_label, lang="en")))
        if self.alt_labels is not None:
            for alt_label in self.alt_labels:
                g.add((c, SKOS.altLabel, Literal(alt_label, lang="en")))
        g.add((c, SKOS.definition, Literal(self.definition, lang="en")))
        if self.children is not None:
            for child in self.children:
                g.add((c, SKOS.narrower, URIRef(child)))
                g.add((URIRef(child), SKOS.broader, c))
        if self.other_ids is not None:
            for other_id in self.other_ids:
                g.add((c, SKOS.notation, Literal(other_id)))
        if self.home_vocab_uri is not None:
            g.add((c, RDFS.isDefinedBy, URIRef(self.home_vocab_uri)))
        if self.provenance is not None:
            g.add((c, DCTERMS.provenance, Literal(self.provenance, lang="en")))

        return g


class Collection(BaseModel):
    uri: AnyHttpUrl
    pref_label: str
    definition: str
    members: List[AnyHttpUrl]
    provenance: str = None

    def to_graph(self):
        g = Graph()
        c = URIRef(self.uri)
        g.add((c, RDF.type, SKOS.Collection))
        g.add((c, SKOS.prefLabel, Literal(self.pref_label, lang="en")))
        g.add((c, SKOS.definition, Literal(self.definition, lang="en")))
        for member in self.members:
            g.add((c, SKOS.member, URIRef(member)))
        if self.provenance is not None:
            g.add((c, DCTERMS.provenance, Literal(self.provenance, lang="en")))

        return g


class Vocabulary(BaseModel):
    concept_scheme: ConceptScheme
    concepts: List[Concept]
    collections: List[Collection]

    def to_graph(self):
        g = self.concept_scheme.to_graph()
        cs = URIRef(self.concept_scheme.uri)
        for concept in self.concepts:
            g += concept.to_graph()
            g.add((URIRef(concept.uri), SKOS.inScheme, cs))
        for collection in self.collections:
            g += collection.to_graph()
            g.add((URIRef(collection.uri), DCTERMS.isPartOf, cs))
            g.add((cs, DCTERMS.hasPart, URIRef(collection.uri)))

        # create as Top Concepts those Concepts that have no skos:narrower properties with them as objects
        for s in g.subjects(SKOS.inScheme, cs):
            is_tc = True
            for o in g.objects(s, SKOS.broader):
                is_tc = False
            if is_tc:
                g.add((cs, SKOS.hasTopConcept, s))
                g.add((s, SKOS.topConceptOf, cs))

        return g
