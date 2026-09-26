import discord, sys, os, asyncio
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import BotConfig

BASE_DIR = Path(__file__).parent
env_path = BASE_DIR / "shared.env"
load_dotenv(env_path)

# Настройки бота
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True
intents.moderation = True
intents.presences = True
bot = commands.Bot(command_prefix=BotConfig.COMMAND_PREFIX, intents=intents, max_messages=1000)

_synced = False  # Флаг синхронизации команд

# ========== ЗАПУСК БОТА ==========

async def sync_commands():
    try:
        if BotConfig.GUILD_ID:

            print("application_id =", bot.application_id)
            print("user =", bot.user)
            print("guild =", guild.id)

            guild = discord.Object(
                id=BotConfig.GUILD_ID
            )

            # Копируем команды из глобального дерева
            # в дерево конкретного сервера.
            bot.tree.copy_global_to(
                guild=guild
            )

            # Публикуем команды на сервере.
            synced = await bot.tree.sync(
                guild=guild
            )

            print(
                "========================================="
            )
            print(
                "⚙️ [ЛОКАЛЬНАЯ СИНХРОНИЗАЦИЯ]"
            )
            print(
                f"Сервер: {guild.id}"
            )
            print(
                f"Успешно синхронизировано команд: "
                f"{len(synced)}"
            )

            for command in synced:
                print(
                    f"   └─ /{command.name}"
                )

        else:

            # Глобальная синхронизация
            synced = await bot.tree.sync()

            print(
                "========================================="
            )
            print(
                "⚙️ [ГЛОБАЛЬНАЯ СИНХРОНИЗАЦИЯ]"
            )
            print(
                f"Успешно синхронизировано команд: "
                f"{len(synced)}"
            )

            for command in synced:
                print(
                    f"   └─ /{command.name}"
                )

    except discord.HTTPException as e:
        print(
            f"❌ Ошибка Discord API "
            f"при синхронизации команд: {e}"
        )

    except discord.Forbidden as e:
        print(
            f"❌ Discord отклонил синхронизацию: {e}"
        )

    except discord.app_commands.CommandSyncFailure as e:
        print(
            f"❌ Ошибка структуры application command: {e}"
        )

    except Exception as e:
        print(
            f"❌ Неизвестная ошибка синхронизации: "
            f"{type(e).__name__}: {e}"
        )

async def load_extensions():
    cogs_dir = BASE_DIR / "cogs"

    if not cogs_dir.exists():
        print(
            f"❌ Папка Cogs не найдена: {cogs_dir}"
        )
        return

    for filename in os.listdir(cogs_dir):

        # Игнорируем __pycache__, __init__.py и т.п.
        if not filename.endswith(".py"):
            continue

        if filename.startswith("_"):
            continue

        cog_name = f"cogs.{filename[:-3]}"

        try:

            await bot.load_extension(cog_name)

            print(
                f"✅ Модуль {cog_name} "
                f"успешно загружен."
            )

        except Exception as e:

            print(
                f"❌ Ошибка загрузки модуля "
                f"{cog_name}: "
                f"{type(e).__name__}: {e}"
            )


async def main():
    token = os.getenv("BOT_TOKEN")

    if not token:
        print(
            "❌ Ошибка: переменная среды "
            "BOT_TOKEN не установлена!"
        )
        return

    async with bot:
        await load_extensions()
        await bot.start(token)

@bot.event
async def on_ready():
    global _synced

    print("=========================================")
    print(f"Бот запущен: {bot.user} ({bot.user.id})")

    if not _synced:
        try:
            guild = discord.Object(id=BotConfig.GUILD_ID)

            print(f"application_id = {bot.application_id}")

            bot.tree.copy_global_to(guild=guild)

            synced = await bot.tree.sync(
                guild=guild
            )

            print(
                f"⚙️ Синхронизировано команд: "
                f"{len(synced)}"
            )

            _synced = True

        except Exception as e:
            print(
                f"❌ Ошибка синхронизации: "
                f"{type(e).__name__}: {e}"
            )
            
    print("=========================================")

    await bot.change_presence(
        activity=discord.CustomActivity(
            name="𝓬𝓲𝓻𝓬𝓾𝓵𝓪𝓽𝓮 𝓪 𝓬𝓾𝓵𝓽𝓲𝓼𝓽 𝓮𝓬𝓸𝓷𝓸𝓶𝓲𝓬𝓼 😈",
        )
    )

if __name__ == "__main__":
    asyncio.run(main())