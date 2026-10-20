import logging
import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(
    BASE_DIR / ".env"
)


# =========================================================
# LOGGING
# =========================================================

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO"
).upper()

logging.basicConfig(
    level=getattr(
        logging,
        LOG_LEVEL,
        logging.INFO
    ),
    format=(
        "%(asctime)s [%(levelname)s] "
        "%(name)s: %(message)s"
    )
)

logger = logging.getLogger(
    "ontologia_iot"
)


# =========================================================
# OPENAI
# =========================================================

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY"
)

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-4o-mini"
)

OPENAI_TEMPERATURE = float(
    os.getenv(
        "OPENAI_TEMPERATURE",
        "0.1"
    )
)

OPENAI_MAX_TOKENS = int(
    os.getenv(
        "OPENAI_MAX_TOKENS",
        "3500"
    )
)

OPENAI_TOP_P = float(
    os.getenv(
        "OPENAI_TOP_P",
        "0.95"
    )
)

OPENAI_FREQUENCY_PENALTY = float(
    os.getenv(
        "OPENAI_FREQUENCY_PENALTY",
        "0.1"
    )
)

OPENAI_PRESENCE_PENALTY = float(
    os.getenv(
        "OPENAI_PRESENCE_PENALTY",
        "0.1"
    )
)

OPENAI_TIMEOUT = float(
    os.getenv(
        "OPENAI_TIMEOUT",
        "90"
    )
)


# =========================================================
# ONTOLOGIA
# =========================================================

ONTOLOGY_FILE = Path(
    os.getenv(
        "ONTOLOGY_FILE",
        BASE_DIR / "ontologias" / "iot.owl"
    )
)

SPARQL_DIRECTORY = Path(
    os.getenv(
        "SPARQL_DIRECTORY",
        BASE_DIR / "queries"
    )
)

SENSOR_CLASS_URI = os.getenv(
    "SENSOR_CLASS_URI"
)