# =========================================================
# SERVICES/FORM_SERVICE.PY
# =========================================================
# MOVER PARA:
#
# services/
# └── form_service.py
#
# Responsabilidade:
# - criar campos do formulário
# - pegar valores enviados pelo formulário
# =========================================================

from config.config import logger


def build_form_fields(ontologia):
    campos = []
    valores_default = {}

    properties = ontologia.get("properties", {})

    logger.info(
        "Construindo campos do formulário a partir de 'properties'."
    )

    for campo, info in properties.items():

        if not isinstance(info, dict):
            continue

        if info.get("editable") is False:
            continue

        valor = info.get("value", "")
        tipo_original = info.get("type", "string")

        # Converte listas de bibliotecas, pinos etc. para texto
        if isinstance(valor, list):
            valor_exibicao = ", ".join(
                map(str, valor)
            )
        else:
            valor_exibicao = str(valor)

        # Objetos da ontologia são contexto técnico:
        # aparecem, mas o aluno/usuário não deve alterá-los
        somente_leitura = tipo_original == "object"

        opcoes = ",".join(
            map(
                str,
                info.get(
                    "allowedValues",
                    info.get("items", [])
                )
            )
        )

        campos.append({
            "Campo": campo,
            "Tipo": (
                "string"
                if somente_leitura
                else tipo_original
            ),
            "Descrição": info.get(
                "description",
                ""
            ),
            "Opções": opcoes,
            "SomenteLeitura": somente_leitura
        })

        valores_default[campo] = valor_exibicao

    campos.append({
        "Campo": "hasTestMode",
        "Tipo": "string",
        "Descrição": "Modo de execução dos testes",
        "Opções": "Hardware Físico, Simulação por Mock",
        "SomenteLeitura": False
    })

    valores_default["hasTestMode"] = "Mock"

    return campos, valores_default


def collect_form_answers(campos, request_form):
    respostas = {}

    logger.info("Coletando respostas enviadas pelo formulário HTTP POST.")

    for c in campos:
        nome_campo = c["Campo"]

        valor_bruto = request_form.get(
            nome_campo
        )

        respostas[nome_campo] = valor_bruto

        logger.debug(
            "Resposta capturada -> %s: %s",
            nome_campo,
            valor_bruto
        )

    return respostas