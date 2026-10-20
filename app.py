from flask import Flask, render_template, request

from config.config import logger
from services.ontology_service import load_ontologies
from forms.form_service import (
    build_form_fields,
    collect_form_answers
)
from prompts.test_generation_prompt import build_prompt
from services.openai_service import generate_code


app = Flask(__name__)

# O serviço carrega o OWL e executa as consultas SPARQL.
ontologias = load_ontologies()


@app.route("/")
def home():
    logger.info("Acessando a rota Home (/).")

    # Passa a usar os sensores recuperados do OWL.
    plataformas = {
        "Arduino": [
            sensor_name
            for sensor_name, sensor_info
            in ontologias.items()
            if (sensor_info
                .get("properties", {})
                .get("hasPlatform", {})
                .get("value")
                == "Arduino"
            )
        ]
    }

    return render_template("home.html",plataformas=plataformas)


@app.route("/sensor/<sensor>",methods=["GET", "POST"])
def formulario(sensor):
    logger.info("Rota /sensor/%s chamada com método: %s",sensor,request.method)

    ontologia = ontologias.get(sensor)

    if ontologia is None:
        logger.error("Ontologia não encontrada: %s",sensor)

        return (f"Ontologia para {sensor} não encontrada.",404)

    campos, valores_default = build_form_fields(ontologia)

    if request.method == "POST":
        try:
            respostas = collect_form_answers(campos,request.form)

            prompt = build_prompt(sensor,ontologia,campos,respostas)

            codigo = generate_code(prompt)

            return render_template("resultado.html",codigo=codigo,ontologia=sensor)

        except Exception as err:
            logger.exception("Erro no fluxo POST do sensor '%s': %s",sensor,err)

            return ("Ocorreu um erro interno ao processar ""a geração. Consulte os logs.",500)

    return render_template("formulario.html",ontologia=sensor,campos=campos,valores_default=valores_default)


@app.route("/plataforma/<nome>")
def ver_plataforma(nome):
    logger.info("Plataforma solicitada: %s",nome)

    sensores = []

    for sensor_name, sensor_info in ontologias.items():
        plataforma = (sensor_info.get("properties", {}).get("hasPlatform", {}).get("value"))

        if plataforma == nome:
            sensores.append(sensor_name)

    return render_template("plataforma.html",nome=nome,sensores=sensores)


if __name__ == "__main__":
    logger.info("Iniciando o servidor Flask de Ontologia IoT.")

    app.run(debug=True,use_reloader=False)