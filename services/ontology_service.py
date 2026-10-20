import logging
import os
from pathlib import Path
from typing import Any
from dotenv import load_dotenv
from rdflib import Graph, Literal, URIRef

logger = logging.getLogger("ontology_service")

BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega as variáveis do arquivo .env
load_dotenv(BASE_DIR / ".env")

ONTOLOGIA_PATH = Path(
    os.getenv(
        "ONTOLOGIA_PATH",
        BASE_DIR / "ontologias" / "iot.xml"
    )
)

QUERIES_PATH = Path(
    os.getenv(
        "SPARQL_QUERIES_PATH",
        BASE_DIR / "queries"
    )
)

SENSOR_CLASS_URI = os.getenv(
    "SENSOR_CLASS_URI"
)



def local_name(value: Any) -> str:
    """
    Retorna somente o nome local de uma URI.

    Exemplo:
    http://exemplo.org/iot#DS18B20 -> DS18B20
    """

    text = str(value)

    if "#" in text:
        return text.rsplit("#", 1)[-1]

    return text.rstrip("/").rsplit("/", 1)[-1]


def load_query(filename: str) -> str:
    """
    Carrega uma consulta SPARQL armazenada em arquivo.
    """

    query_path = QUERIES_PATH / filename

    if not query_path.exists():
        raise FileNotFoundError(
            f"Consulta SPARQL não encontrada: "
            f"{query_path.resolve()}"
        )

    return query_path.read_text(
        encoding="utf-8"
    )


def load_graph() -> Graph:
    """
    Carrega o arquivo OWL em um grafo RDFLib.
    """

    if not ONTOLOGIA_PATH.exists():
        raise FileNotFoundError(
            f"Arquivo OWL não encontrado: "
            f"{ONTOLOGIA_PATH.resolve()}"
        )

    graph = Graph()

    graph.parse(
        source=str(ONTOLOGIA_PATH)
    )

    logger.info(
        "Ontologia carregada: %s",
        ONTOLOGIA_PATH.resolve()
    )

    logger.info(
        "Quantidade de triplas: %d",
        len(graph)
    )

    return graph


def convert_literal(value: Literal) -> Any:
    """
    Converte um Literal RDF para um tipo Python.
    """

    converted = value.toPython()

    if converted is None:
        return str(value)

    return converted


def convert_value(value: Any) -> Any:
    """
    Converte literais e recursos RDF em valores simples.
    """

    if isinstance(value, Literal):
        return convert_literal(value)

    if isinstance(value, URIRef):
        return local_name(value)

    return str(value)


def identify_property_type(value: Any) -> str:
    """
    Determina o tipo usado pelo formulário.
    """

    if isinstance(value, URIRef):
        return "object"

    if not isinstance(value, Literal):
        return "string"

    python_value = value.toPython()

    if isinstance(python_value, bool):
        return "boolean"

    if isinstance(python_value, int):
        return "integer"

    if isinstance(python_value, float):
        return "number"

    return "string"


def append_property(
    properties: dict,
    property_name: str,
    value: Any,
    property_type: str
) -> None:
    """
    Adiciona uma propriedade e trata propriedades multivaloradas.
    """

    if property_name not in properties:
        properties[property_name] = {
            "type": property_type,
            "value": value
        }

        return

    current_value = properties[
        property_name
    ]["value"]

    if not isinstance(current_value, list):
        current_value = [current_value]

    if value not in current_value:
        current_value.append(value)

    properties[property_name]["value"] = (
        current_value
    )


def list_sensors(graph: Graph) -> list[dict]:
    """
    Executa a consulta que lista os sensores.
    """

    if not SENSOR_CLASS_URI:
        raise ValueError(
            "A variável SENSOR_CLASS_URI não foi definida."
        )

    query = load_query(
        "listar_sensores.rq"
    )

    results = graph.query(
        query,
        initBindings={
            "sensorBaseClass": URIRef(
                SENSOR_CLASS_URI
            )
        }
    )

    sensors = {}

    for row in results:
        sensor_uri = row.sensor
        sensor_name = local_name(sensor_uri)

        if sensor_name not in sensors:
            sensors[sensor_name] = {
                "name": sensor_name,
                "uri": str(sensor_uri),
                "type": local_name(
                    row.sensorType
                ),
                "label": (
                    str(row.label)
                    if row.label is not None
                    else sensor_name
                ),
                "description": (
                    str(row.description)
                    if row.description is not None
                    else ""
                )
            }

    return list(sensors.values())


def get_sensor_properties(graph: Graph,sensor_uri: str) -> dict:
    """
    Recupera as propriedades de um sensor.
    """

    query = load_query("dados_sensor.rq")

    results = graph.query(
        query,initBindings={"sensor": URIRef(sensor_uri)}
    )

    properties = {}

    for row in results:
        property_name = local_name(
            row.property
        )

        property_value = convert_value(
            row.value
        )

        property_type = identify_property_type(
            row.value
        )

        append_property(
            properties=properties,
            property_name=property_name,
            value=property_value,
            property_type=property_type
        )

    return properties


def get_sensor_restrictions(
    graph: Graph,
    sensor_uri: str
) -> dict:
    """
    Lê bibliotecas, pinos, protocolo, unidade,
    framework de teste e demais restrições OWL.
    """

    query = load_query("restricoes_sensor.rq")

    results = graph.query(
        query,
        initBindings={
            "sensor": URIRef(sensor_uri)
        }
    )

    properties = {}

    for row in results:
        property_name = local_name(row.property)
        property_value = convert_value(row.value)

        append_property(
            properties=properties,
            property_name=property_name,
            value=property_value,
            property_type="object"
        )

    return properties


def merge_properties(
    target: dict,
    source: dict
) -> None:
    """
    Inclui as restrições OWL nas propriedades
    já lidas diretamente do indivíduo.
    """

    for property_name, data in source.items():
        values = data["value"]

        if not isinstance(values, list):
            values = [values]

        for value in values:
            append_property(
                properties=target,
                property_name=property_name,
                value=value,
                property_type=data["type"]
            )


def get_sensor_hierarchy(graph: Graph,sensor_uri: str) -> list[str]:
    """
    Recupera a hierarquia de classes de um sensor.
    """

    query = load_query("hierarquia_sensor.rq")

    results = graph.query(query,initBindings={"sensor": URIRef(sensor_uri)})

    hierarchy = []

    for row in results:
        sensor_class = local_name(row.sensorClass)

        super_class = local_name(row.superClass)

        if sensor_class not in hierarchy:
            hierarchy.append(sensor_class)

        if super_class not in hierarchy:
            hierarchy.append(super_class)

    return hierarchy


def load_ontologies() -> dict:
    """
    Função principal chamada pela aplicação Flask.

    Converte os resultados do OWL/SPARQL para a
    estrutura de dicionários esperada pelo restante
    da aplicação.
    """

    logger.info("=" * 80)
    logger.info("CARREGANDO ONTOLOGIA OWL")
    logger.info("=" * 80)

    graph = load_graph()
    sensors = list_sensors(graph)

    ontologies = {}

    for sensor in sensors:
        sensor_name = sensor["name"]
        sensor_uri = sensor["uri"]

        logger.info("Processando sensor: %s",sensor_name)

        properties = get_sensor_properties(graph,sensor_uri)

        restrictions = get_sensor_restrictions(
            graph,
            sensor_uri
        )

        merge_properties(
            properties,
            restrictions
        )


        hierarchy = get_sensor_hierarchy(graph,sensor_uri)

        ontologies[sensor_name] = {
            "uri": sensor_uri,
            "description": sensor[
                "description"
            ],
            "properties": properties,
            "ontologyMapping": {
                "classHierarchy": hierarchy
            }
        }

    logger.info("Sensores carregados: %s",list(ontologies.keys()))

    return ontologies