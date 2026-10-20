from openai import OpenAI

from config.config import (
    logger,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
    OPENAI_MAX_TOKENS,
    OPENAI_TOP_P,
    OPENAI_FREQUENCY_PENALTY,
    OPENAI_PRESENCE_PENALTY,
    OPENAI_TIMEOUT
)


def create_openai_client() -> OpenAI:
    """
    Cria e configura o cliente da OpenAI.
    """

    if not OPENAI_API_KEY:
        raise RuntimeError(
            "A variável OPENAI_API_KEY não foi "
            "definida no arquivo .env."
        )

    return OpenAI(
        api_key=OPENAI_API_KEY,
        timeout=OPENAI_TIMEOUT
    )


def generate_code(prompt: str) -> str:
    """
    Envia o prompt para a OpenAI e retorna
    o código gerado.
    """

    if not prompt or not prompt.strip():
        raise ValueError(
            "O prompt não pode ser vazio."
        )

    logger.info(
        "Chamando a OpenAI com o modelo: %s",
        OPENAI_MODEL
    )

    logger.info(
        "Tamanho do prompt: %d caracteres",
        len(prompt)
    )

    logger.debug(
        "Prompt enviado à LLM:\n%s",
        prompt
    )

    try:
        client = create_openai_client()

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um gerador de testes "
                        "funcionais para firmware de "
                        "dispositivos IoT. Gere apenas "
                        "o código C++/Arduino solicitado, "
                        "sem explicações adicionais."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=OPENAI_TEMPERATURE,
            max_tokens=OPENAI_MAX_TOKENS,
            top_p=OPENAI_TOP_P,
            frequency_penalty=(
                OPENAI_FREQUENCY_PENALTY
            ),
            presence_penalty=(
                OPENAI_PRESENCE_PENALTY
            )
        )

        if not response.choices:
            raise RuntimeError(
                "A OpenAI não retornou alternativas."
            )

        content = (
            response
            .choices[0]
            .message
            .content
        )

        if content is None:
            raise RuntimeError(
                "A OpenAI retornou conteúdo vazio."
            )

        generated_code = content.strip()

        if not generated_code:
            raise RuntimeError(
                "O código gerado está vazio."
            )

        logger.info(
            "Resposta recebida com sucesso."
        )

        logger.info(
            "Tamanho do código: %d caracteres",
            len(generated_code)
        )

        if response.usage:
            logger.info(
                "Tokens de entrada: %s",
                response.usage.prompt_tokens
            )

            logger.info(
                "Tokens de saída: %s",
                response.usage.completion_tokens
            )

            logger.info(
                "Total de tokens: %s",
                response.usage.total_tokens
            )

        logger.debug(
            "Código gerado:\n%s",
            generated_code
        )

        if len(generated_code) < 50:
            logger.warning(
                "O código gerado possui menos "
                "de 50 caracteres."
            )

        if "#include" not in generated_code:
            logger.warning(
                "O código gerado não possui #include."
            )

        return generated_code

    except Exception:
        logger.exception(
            "Falha ao gerar código usando a OpenAI."
        )

        raise