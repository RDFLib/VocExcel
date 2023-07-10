from textwrap import dedent

from fastapi import APIRouter, Body, HTTPException, UploadFile, status
from fastapi.responses import PlainTextResponse
from jinja2 import Template
from rdflib import Graph

from vocexcel.convert import ConversionError, excel_to_rdf
from vocexcel.web.response import TurtleResponse
from vocexcel.web.settings import Settings

router = APIRouter()


@router.get("/version", response_class=PlainTextResponse)
def version_route():
    """VocExcel application version."""
    return Settings.VOCEXCEL_VERSION


@router.post("/convert", response_class=TurtleResponse)
async def convert_route(upload_file: UploadFile):
    """Convert a VocExcel file to RDF Turtle."""
    try:
        file = upload_file.file
        result = excel_to_rdf(file)
        return TurtleResponse(result)
    except ConversionError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        ) from err
    except Exception as err:
        import traceback

        tb = traceback.format_exception(err)
        for item in tb:
            print(item)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error processing the file.",
        ) from err


@router.post("/format", response_class=TurtleResponse)
def format_route(payload: str = Body(media_type="application/n-triples")):
    """Format N-Triples as Turtle in the `longturtle` style."""
    graph = Graph()
    graph.parse(data=payload, format="ntriples")
    return graph.serialize(format="longturtle")


@router.get("/construct-query", response_class=PlainTextResponse)
def construct_query_route(focus_node_iri: str, depth: int):
    """Get the SPARQL Construct query for a given focus node IRI and the depth of the blank nodes in the graph closure."""
    query = Template(
        dedent(
            """\
            CONSTRUCT {
                ?s ?p ?o0 .
                {% for i in range(depth) -%}
                ?o{{ i }} ?p{{ i + 1 }} ?o{{ i + 1 }} .
                {% endfor %}
            }
            WHERE {
                BIND(<{{ resource_id }}> AS ?s)
                ?s ?p ?o0 .
                {% for i in range(depth) %}
                OPTIONAL {
                    {% for j in range(i + 1) -%}
                    ?o{{ j }} ?p{{ j + 1 }} ?o{{ j + 1}}
                    FILTER(isBlank(?o{{ j }}))
                    {% endfor %}
                }
                {%- endfor %}
            }"""
        )
    ).render(resource_id=focus_node_iri, depth=depth)

    return PlainTextResponse(query)
