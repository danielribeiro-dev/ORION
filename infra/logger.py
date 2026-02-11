"""
Infrastructure Logging Module.

Responsabilidade:
    - Configurar e prover logger estruturado.
    - Padronizar formato de logs.

Regras:
    - Saída padrão para STDOUT.
"""

import logging
import sys
from infra.config import settings

def setup_logger(name: str) -> logging.Logger:
    """
    Configura logger:
    - FileHandler: Debug+ (orion.log)
    - StreamHandler: Warning+ (Console, clean config)
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG) # Lowest level for capture
    
    if not logger.handlers:
        # 1. File Handler (Detailed)
        file_handler = logging.FileHandler("orion.log")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # 2. Stream Handler (Clean, Error only)
        # stream_handler = logging.StreamHandler(sys.stdout)
        # stream_handler.setLevel(logging.WARNING) # Only warn/error on console
        # stream_formatter = logging.Formatter(
        #     '[%(levelname)s] %(message)s' # Minimal
        # )
        # stream_handler.setFormatter(stream_formatter)
        # logger.addHandler(stream_handler)
        
    return logger

# Default logger for infra
logger = setup_logger("ORION.Infra")
