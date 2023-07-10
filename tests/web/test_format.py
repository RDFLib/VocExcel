import pytest
from fastapi.testclient import TestClient
from rdflib import Graph
from rdflib.compare import isomorphic


@pytest.mark.parametrize(
    "input_data, expected_output",
    [
        [
            """
            <https://example.com/my-concepts/top> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2004/02/skos/core#Concept> .
            <https://example.com/my-concepts/top> <http://www.w3.org/2000/01/rdf-schema#isDefinedBy> <https://example.com/my-concepts> .
            <https://example.com/my-concepts/top> <http://www.w3.org/2004/02/skos/core#altLabel> "T"@en .
            <https://example.com/my-concepts/top> <http://www.w3.org/2004/02/skos/core#definition> "A top concept."@en .
            <https://example.com/my-concepts/top> <http://www.w3.org/2004/02/skos/core#inScheme> <https://example.com/my-concepts> .
            <https://example.com/my-concepts/top> <http://www.w3.org/2004/02/skos/core#prefLabel> "Top"@en .
            <https://example.com/my-concepts/top> <http://www.w3.org/2004/02/skos/core#narrower> <https://example.com/my-concepts/highway> .
            <https://example.com/my-concepts/top> <http://www.w3.org/2004/02/skos/core#narrower> <https://example.com/my-concepts/motorway> .
            <https://example.com/my-concepts/top> <http://www.w3.org/2004/02/skos/core#narrower> <https://example.com/my-concepts/secondary> .
            <https://example.com/my-concepts/top> <http://www.w3.org/2004/02/skos/core#topConceptOf> <https://example.com/my-concepts> .
            """,
            """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

            <https://example.com/my-concepts/top>
                a skos:Concept ;
                rdfs:isDefinedBy <https://example.com/my-concepts> ;
                skos:altLabel "T"@en ;
                skos:definition "A top concept."@en ;
                skos:inScheme <https://example.com/my-concepts> ;
                skos:narrower
                    <https://example.com/my-concepts/highway> ,
                    <https://example.com/my-concepts/motorway> ,
                    <https://example.com/my-concepts/secondary> ;
                skos:prefLabel "Top"@en ;
                skos:topConceptOf <https://example.com/my-concepts> ;
            .

            """,
        ],
        [
            """
            <https://example.com/my-concepts> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2004/02/skos/core#ConceptScheme> .
            <https://example.com/my-concepts> <http://www.w3.org/2004/02/skos/core#definition> "A vocabulary named My Concepts."@en .
            <https://example.com/my-concepts> <http://www.w3.org/2004/02/skos/core#historyNote> "A vocabulary to test VocExcel."@en .
            <https://example.com/my-concepts> <http://www.w3.org/2004/02/skos/core#prefLabel> "My Concepts"@en .
            <https://example.com/my-concepts> <http://purl.org/dc/terms/created> "2023-07-03"^^<http://www.w3.org/2001/XMLSchema#date> .
            <https://example.com/my-concepts> <http://purl.org/dc/terms/creator> _:bc_0_n3-0 .
            _:bc_0_n3-0 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/ns/prov#Agent> .
            <https://example.com/my-concepts> <http://purl.org/dc/terms/creator> _:bc_0_n3-0 .
            _:bc_0_n3-0 <http://www.w3.org/2000/01/rdf-schema#label> "Edmond Chuc" .
            <https://example.com/my-concepts> <http://purl.org/dc/terms/identifier> "my-concepts"^^<http://www.w3.org/2001/XMLSchema#token> .
            <https://example.com/my-concepts> <http://purl.org/dc/terms/modified> "2023-07-03"^^<http://www.w3.org/2001/XMLSchema#date> .
            <https://example.com/my-concepts> <http://purl.org/dc/terms/publisher> _:bc_0_n3-1 .
            _:bc_0_n3-1 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/ns/prov#Agent> .
            <https://example.com/my-concepts> <http://purl.org/dc/terms/publisher> _:bc_0_n3-1 .
            _:bc_0_n3-1 <http://www.w3.org/2000/01/rdf-schema#label> "Edmond Chuc" .
            <https://example.com/my-concepts> <http://www.w3.org/2002/07/owl#versionIRI> <https://example.com/my-concepts/0.1.0> .
            <https://example.com/my-concepts> <http://www.w3.org/2002/07/owl#versionInfo> "0.1.0" .
            <https://example.com/my-concepts> <http://www.w3.org/ns/prov#qualifiedAttribution> _:bc_0_n3-2 .
            _:bc_0_n3-2 <http://www.w3.org/ns/dcat#hadRole> <http://def.isotc211.org/iso19115/-1/2018/CitationAndResponsiblePartyInformation/code/CI_RoleCode/custodian> .
            <https://example.com/my-concepts> <http://www.w3.org/ns/prov#qualifiedAttribution> _:bc_0_n3-2 .
            _:bc_0_n3-2 <http://www.w3.org/ns/prov#agent> _:bc_0_n3-3 .
            _:bc_0_n3-3 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/ns/prov#Agent> .
            <https://example.com/my-concepts> <http://www.w3.org/ns/prov#qualifiedAttribution> _:bc_0_n3-2 .
            _:bc_0_n3-2 <http://www.w3.org/ns/prov#agent> _:bc_0_n3-3 .
            _:bc_0_n3-3 <http://www.w3.org/2000/01/rdf-schema#label> "Edmond Chuc" .
            """,
            """
            PREFIX dcat: <http://www.w3.org/ns/dcat#>
            PREFIX dcterms: <http://purl.org/dc/terms/>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX prov: <http://www.w3.org/ns/prov#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            <https://example.com/my-concepts>
                a skos:ConceptScheme ;
                dcterms:created "2023-07-03"^^xsd:date ;
                dcterms:creator [
                        a prov:Agent ;
                        rdfs:label "Edmond Chuc"
                    ] ;
                dcterms:identifier "my-concepts"^^xsd:token ;
                dcterms:modified "2023-07-03"^^xsd:date ;
                dcterms:publisher [
                        a prov:Agent ;
                        rdfs:label "Edmond Chuc"
                    ] ;
                owl:versionIRI <https://example.com/my-concepts/0.1.0> ;
                owl:versionInfo "0.1.0" ;
                skos:definition "A vocabulary named My Concepts."@en ;
                skos:historyNote "A vocabulary to test VocExcel."@en ;
                skos:prefLabel "My Concepts"@en ;
                prov:qualifiedAttribution [
                        dcat:hadRole <http://def.isotc211.org/iso19115/-1/2018/CitationAndResponsiblePartyInformation/code/CI_RoleCode/custodian> ;
                        prov:agent [
                                a prov:Agent ;
                                rdfs:label "Edmond Chuc"
                            ]
                    ] ;
            .


            """,
        ],
    ],
)
def test(client: TestClient, input_data: str, expected_output: str):
    headers = {"content-type": "application/n-triples", "accept": "text/turtle"}
    response = client.post("/api/v1/format", content=input_data, headers=headers)

    assert response.status_code == 200

    input_graph = Graph()
    input_graph.parse(data=input_data, format="ntriples")
    expected_graph = Graph()
    expected_graph.parse(data=expected_output)
    assert isomorphic(input_graph, expected_graph)
