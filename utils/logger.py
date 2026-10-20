import logging
import sys
from config.config import Config


def setup_logger():
    """Configura e retorna o logger da aplicação"""
    logger = logging.getLogger("app_ontologia")
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))

    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # Handler para arquivo
    file_handler = logging.FileHandler('app.log', encoding='utf-8')
    file_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(Config.LOG_FORMAT)
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Adiciona handlers se não existirem
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger