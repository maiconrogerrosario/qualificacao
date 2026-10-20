# =========================================================
# APP.PY
# =========================================================
# Este arquivo deve ficar com:
# - criação do Flask
# - rotas
# - coordenação entre os services
# =========================================================

from flask import Flask, render_template, request

# ESTES IMPORTS VIRIAM DOS ARQUIVOS SEPARADOS:
from config.config import logger
from services.ontology_service import load_ontologies
from forms.form_service import build_form_fields, collect_form_answers
from prompts.test_generation_prompt import build_prompt
from services.openai_service import generate_code




app = Flask(__name__)

ontologias = load_ontologies()





@app.route("/")
def home():

    logger.info(
        "Acessando a rota Home (/)."
    )

    plataformas = {
        "Arduino": [
            "DS18B20",
            "HCSR04"
        ],
    }

    return render_template(
        "home.html",
        plataformas=plataformas
    )


@app.route(
    "/sensor/<sensor>",
    methods=["GET", "POST"]
)
def formulario(sensor):

    logger.info(
        "Rota /sensor/%s chamada com método: %s",
        sensor,
        request.method
    )

    ontologia = ontologias.get(sensor)

    if not ontologia:

        logger.error(
            "Ontologia solicitada não encontrada na memória: %s",
            sensor
        )

        return (
            f"Ontologia para {sensor} não encontrada.",
            404
        )

    # =====================================================
    # CHAMA FORM_SERVICE
    # =====================================================

    campos, valores_default = build_form_fields(
        ontologia
    )

    if request.method == "POST":

        try:

            # =============================================
            # CHAMA FORM_SERVICE
            # =============================================

            respostas = collect_form_answers(
                campos,
                request.form
            )

            # =============================================
            # CHAMA PROMPT
            # =============================================

            prompt = build_prompt(
                sensor,
                ontologia,
                campos,
                respostas
            )

            # =============================================
            # CHAMA OPENAI_SERVICE
            # =============================================

            codigo = generate_code(
                prompt
            )

            return render_template(
                "resultado.html",
                codigo=codigo,
                ontologia=sensor
            )

        except Exception as err:

            logger.exception(
                "Erro crítico no fluxo POST do sensor '%s': %s",
                sensor,
                err
            )

            return (
                "Ocorreu um erro interno ao processar a geração. "
                "Detalhes salvos nos logs de execução.",
                500
            )

    return render_template(
        "formulario.html",
        ontologia=sensor,
        campos=campos,
        valores_default=valores_default
    )


@app.route("/plataforma/<nome>")
def ver_plataforma(nome):

    logger.info(
        "Rota de visualização por plataforma acionada: %s",
        nome
    )

    sensores = []

    for sensor_name, sensor_info in ontologias.items():

        plataforma = (
            sensor_info
            .get("properties", {})
            .get("hasPlatform", {})
            .get("value")
        )

        if plataforma == nome:
            sensores.append(
                sensor_name
            )

    logger.debug(
        "Sensores encontrados para a plataforma '%s': %s",
        nome,
        sensores
    )

    return render_template(
        "plataforma.html",
        nome=nome,
        sensores=sensores
    )


# =========================================================
# APP.PY
# =========================================================
# INICIALIZAÇÃO DO SERVIDOR CONTINUA NO APP.PY
# =========================================================

if __name__ == "__main__":

    logger.info(
        "Iniciando o servidor Flask de Ontologia IoT..."
    )

    app.run(
        debug=True,
        use_reloader=False

    )