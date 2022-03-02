import pytest
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.absolute()))
from vocexcel.models import *
from pydantic.error_wrappers import ValidationError


def test_vocabulary_valid():
    v = ConceptScheme(
        uri="https://linked.data.gov.au/def/borehole-start-point",
        title="Borehole Start Point",
        description="Indicates the nature of the borehole start point location",
        created="2020-04-02",
        modified="2020-04-02",
        creator="GSQ",
        publisher="GSQ",
        version="",
        provenance="Derived from the 2011-09 version of CGI Borehole start point list",
        custodian="Vance Kelly",
        pid="http://pid.geoscience.gov.au/dataset/ga/114541",
    )


def test_vocabulary_invalid_uri():
    with pytest.raises(ValidationError):
        v = ConceptScheme(
            uri="ftp://linked.data.gov.au/def/borehole-start-point",
            title="Borehole Start Point",
            description="Indicates the nature of the borehole start point location",
            created="2020-04-02",
            modified="02/042020",
            creator="GSQ",
            publisher="GSQ",
            version="",
            provenance="Derived from the 2011-09 version of CGI Borehole start point list",
            custodian="Vance Kelly",
            pid="http://pid.geoscience.gov.au/dataset/ga/114541",
        )


def test_vocabulary_invalid_created_date():
    with pytest.raises(ValidationError):
        v = ConceptScheme(
            uri="https://linked.data.gov.au/def/borehole-start-point",
            title="Borehole Start Point",
            description="Indicates the nature of the borehole start point location",
            created="2020-04",
            modified="2020-04-02",
            creator="GSQ",
            publisher="GSQ",
            version="",
            provenance="Derived from the 2011-09 version of CGI Borehole start point list",
            custodian="Vance Kelly",
            pid="http://pid.geoscience.gov.au/dataset/ga/114541",
        )


def test_vocabulary_invalid_publisher():
    with pytest.raises(ValidationError):
        v = ConceptScheme(
            uri="https://linked.data.gov.au/def/borehole-start-point",
            title="Borehole Start Point",
            description="Indicates the nature of the borehole start point location",
            created="2020-04-02",
            modified="2020-04-02",
            creator="GSQ",
            publisher="WHO",
            version="",
            provenance="Derived from the 2011-09 version of CGI Borehole start point list",
            custodian="Vance Kelly",
            pid="http://pid.geoscience.gov.au/dataset/ga/114541",
        )


def test_concept():
    # uri
    # pref_label
    # alt_labels
    # pl_language_code
    # definition
    # def_language_code
    # children
    # other_ids
    # home_vocab_uri
    # provenance
    c = Concept(
        uri="https://example.com/thing/x",
        pref_label="Thing X",
        definition="Fake def for Thing X",
    )
    print(c.to_graph().serialize())


def test_concept_iri():
    # this is testing that children list elements are IRIs, not just ordinary strings
    # uri
    # pref_label
    # alt_labels
    # pl_language_code
    # definition
    # def_language_code
    # children
    # other_ids
    # home_vocab_uri
    # provenance
    with pytest.raises(ValidationError) as e:
        c = Concept(
            uri="https://example.com/thing/x",
            pref_label="Thing X",
            definition="Fake def for Thing X",
            children=["broken iri", "http://example.com/working-iri"],  # non-IRI string
        )

    with pytest.raises(ValidationError) as e:
        c = Concept(
            uri="https://example.com/thing/x",
            pref_label="Thing X",
            definition="Fake def for Thing X",
            children=[
                "ftp://example.com/working-iri",
                "http://example.com/working-iri",
            ],  # IRI starts ftp
        )

    with pytest.raises(ValidationError) as e:
        c = Concept(
            uri="https://example.com/thing/x",
            pref_label="Thing X",
            definition="Fake def for Thing X",
            children=[
                "http://example.com/ working-iri",
                "http://example.com/working-iri",
            ],  # space in IRI
        )

    # valid children, invalid related_match
    with pytest.raises(ValidationError) as e:
        c = Concept(
            uri="https://example.com/thing/x",
            pref_label="Thing X",
            definition="Fake def for Thing X",
            related_match=[
                "http://example.com/working-iri/rm/1",
                "http://example.com/working-iri/rm/ 2",  # space
                "ftp://example.com/working-iri/rm/3",  # starts ftp
            ],
            children=[
                "http://example.com/working-iri/c/1",
                "http://example.com/working-iri/c/2",
            ],
        )
    print(e)
