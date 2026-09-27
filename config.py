import os
from pathlib import Path
from discord import app_commands

BASE_DIR = Path(__file__).parent

class BotConfig:
    # =============== DB PATH ===============
    DB_PATH = str(BASE_DIR / "database" / "econ_hope.db")
    
    # =============== VARIABLES ===============
    GUILD_ID = 1550405259770335375
    DEVELOPER_ID = 777122004376879115
    COMMAND_PREFIX = '/'

    COMMAND_CHANNEL = 1550428642184790148
    LOG_CHANNEL = 1553329406993502218

    TRANSACTIONS_AVAILABLE = True