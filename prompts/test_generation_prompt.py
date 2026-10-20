# =========================================================
# TEST_GENERATION_PROMPT.PY
# =========================================================
# Responsável por construir o prompt enviado à LLM
# para geração dos casos de teste.
# =========================================================

import json

from config.config import logger


# =========================================================
# DESCRIÇÕES DOS MODOS DE TESTE
# =========================================================

TEST_MODE_DESCRIPTIONS = {

    "Hardware Físico":
        "Utilize as informações fornecidas pela ontologia e gere testes "
        "que interajam com o sensor físico real conectado à plataforma alvo.",

    "Simulação por Mock":
        "Utilize as informações fornecidas pela ontologia e gere testes "
        "simulados por meio de mocks, sem depender da presença física do sensor.",
}


# =========================================================
# CONSTRUÇÃO DO PROMPT
# =========================================================

def build_prompt(sensor, ontologia, campos, respostas):

    logger.debug(
        "Construindo prompt para o sensor: %s",
        sensor
    )

    # =====================================================
    # MODO DE TESTE SELECIONADO
    # =====================================================

    modo_teste = respostas.get(
        "hasTestMode",
        "Fisico E Mock"
    )

    logger.debug(
        "Valor de modo_teste: %s",
        modo_teste
    )

    # Obtém a descrição correspondente ao modo selecionado
    descricao_modo = TEST_MODE_DESCRIPTIONS.get(
        modo_teste,
        "Modo de teste não especificado."
    )

    logger.debug(
        "Descrição do modo de teste: %s",
        descricao_modo
    )

    # =====================================================
    # CONVERSÃO DA ONTOLOGIA PARA JSON
    # =====================================================

    ontologia_json = json.dumps(
        ontologia,
        indent=2,
        ensure_ascii=False
    )

    # =====================================================
    # PARÂMETROS SELECIONADOS PELO USUÁRIO
    # =====================================================

    parametros = "\n".join(
        f"- {campo['Campo']}: "
        f"{respostas.get(campo['Campo'])}"
        for campo in campos
    )

    # =====================================================
    # PROMPT
    # =====================================================

    prompt = f"""
Contexto:
Com base nas informações fornecidas, gerar casos de teste automatizados para validar o comportamento do componente físico do sensor {sensor}, considerando sua integração com a plataforma alvo.
Parâmetros selecionados pelo usuário:

Ontologia (fonte de conhecimento do domínio):
{ontologia_json}

{parametros}

Modo de teste selecionado:
{modo_teste}

Descrição do modo de teste:
{descricao_modo}


""".strip()

    # =====================================================
    # LOGS
    # =====================================================

    logger.debug(
        "Modo de teste: %s",
        modo_teste
    )

    logger.debug(
        "Tamanho do prompt: %d caracteres",
        len(prompt)
    )

    logger.debug(
        "Prompt enviado:\n%s",
        prompt
    )

    return prompt