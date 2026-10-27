import os
from pathlib import Path
from discord import app_commands

BASE_DIR = Path(__file__).parent

class BotConfig:
    # =============== DB PATH ===============
    DB_PATH = str(BASE_DIR / "database" / "econ_hope.db")
    
    # =============== VARIABLES ===============
    GUILD_ID = 1514703710419419197
    DEVELOPER_ID = 777122004376879115
    COMMAND_PREFIX = '/'

    COMMAND_CHANNEL = 1514703710930997250
    LOG_CHANNEL = 1519742815024709752

    TRANSACTIONS_AVAILABLE = True