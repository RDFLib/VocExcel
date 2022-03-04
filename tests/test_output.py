from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.absolute()))
from vocexcel import convert
from rdflib import URIRef
from rdflib.namespace import SKOS


def test_example_complex():
    g = convert.excel_to_rdf(
        Path(__file__).parent.parent / "templates" / "VocExcel-template_030.xlsx",
        sheet_name="example - complex",
        output_type="graph",
    )

    top_concepts = 0
    for s, o in g.subject_objects(SKOS.topConceptOf):
        top_concepts += 1
    assert top_concepts == 3, (
        f'Processing the test vocab ("example - complex" sheet in workbook '
        f"VocExcel-template.ttl) has yielded {top_concepts} top concepts but it should have "
        f"yielded 3"
    )

    for o in g.objects(
        URIRef(
            "http://resource.geosciml.org/classifierscheme/cgi/2016.01/particletype"
        ),
        SKOS.prefLabel,
    ):
        assert str(o) == "Particle Type", (
            f'The title (preferredLabel) of the "example - complex" sheet vocab in '
            f'the VocExcel-template.ttl is {s} but should be "Particle Type"'
        )


if __name__ == "__main__":
    test_example_complex()
