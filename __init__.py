from flask import Flask
from app.utils.logger import setup_logger
from config.config import Config


def create_app(config_class=Config):
    """Factory pattern para criação da aplicação Flask"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configuração do logger
    logger = setup_logger()
    app.logger = logger

    # Registrar blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app