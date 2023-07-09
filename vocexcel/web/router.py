from textwrap import dedent

from fastapi import APIRouter, UploadFile, HTTPException, status, Body
from fastapi.responses import PlainTextResponse
from rdflib import Graph
from jinja2 import Template

from vocexcel.convert import excel_to_rdf
from vocexcel.web.response import TurtleResponse
from vocexcel.web.settings import Settings

router = APIRouter()


@router.get("/version", response_class=PlainTextResponse)
def version_route():
    return Settings.VOCEXCEL_VERSION


@router.post("/convert", response_class=TurtleResponse)
async def convert_route(upload_file: UploadFile):
    try:
        file = upload_file.file
        result = excel_to_rdf(file)
        return TurtleResponse(result)
    except Exception as err:
        import traceback

        tb = traceback.format_exception(err)
        print(tb)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error processing the file.",
        ) from err


@router.post("/format", response_class=TurtleResponse)
def format_route(payload: str = Body(media_type="application/n-triples")):
    graph = Graph()
    graph.parse(data=payload, format="ntriples")
    return graph.serialize(format="longturtle")


@router.get("/construct-query")
def construct_query_route(focus_node_iri: str, depth: int):
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
