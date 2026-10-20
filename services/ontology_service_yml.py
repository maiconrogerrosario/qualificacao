# =========================================================
# SERVICES/ONTOLOGY_SERVICE.PY
# =========================================================
# MOVER PARA:
#
# services/
# └── ontology_service.py
#
# Responsabilidade:
# - buscar arquivos YAML
# - carregar ontologias
# - devolver dicionário com ontologias
# =========================================================
import glob
import os
import yaml
from config.config import logger




def load_ontologies(path="./ontologias/"):
    ontologias = {}

    arquivos = (
        glob.glob(os.path.join(path, "*.yaml"))
        + glob.glob(os.path.join(path, "*.yml"))
    )

    logger.info(
        "Buscando arquivos de ontologia na pasta: %s",
        path
    )

    logger.info(
        "Arquivos encontrados: %s",
        arquivos
    )

    for arquivo in arquivos:
        try:
            with open(
                arquivo,
                "r",
                encoding="utf-8"
            ) as f:
                data = yaml.safe_load(f)

            if isinstance(data, dict):
                for k, v in data.items():
                    ontologias[k] = v

                    logger.info(
                        "Ontologia '%s' carregada com sucesso do arquivo: %s",
                        k,
                        os.path.basename(arquivo)
                    )

            else:
                logger.warning(
                    "O arquivo '%s' não possui um objeto válido na raiz.",
                    arquivo
                )

        except Exception as e:
            logger.error(
                "Erro ao ler o arquivo '%s': %s",
                arquivo,
                e,
                exc_info=True
            )

    logger.info(
        "Total de ontologias em memória: %s",
        list(ontologias.keys())
    )

    return ontologias