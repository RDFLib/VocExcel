from fastapi.testclient import TestClient
from rdflib import Graph


def test(client: TestClient):
    with open("tests/062_simple1.xlsx", "rb") as file:
        files = {"upload_file": file}
        response = client.post("/api/v1/convert", files=files)

        assert response.status_code == 200
        assert "text/turtle" in response.headers.get("content-type")

        graph = Graph()
        graph.parse(data=response.text)
        assert len(graph) > 0
