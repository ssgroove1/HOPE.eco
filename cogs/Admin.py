import discord
from discord import app_commands
from pathlib import Path
from discord.ext import commands

# Импорт ваших собственных настроек и функций из корня проекта
from config import BotConfig
from database.db_logic import DB_Manager

# Корень проекта (поднимаемся из папки cogs/ на один уровень вверх)
BASE_DIR = Path(__file__).resolve().parent.parent

# COMPANENT: Компанент простого текстового сообщения
class DefaultComponent(discord.ui.LayoutView):
    def __init__(
        self,
        content,
    ):
        super().__init__()
        self.InfoContainer = discord.ui.Container(
            discord.ui.TextDisplay(content=content),
        )
        self.add_item(self.InfoContainer)

# LOGIC: Основной функционал админ ф-ций
class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.manager = DB_Manager(BotConfig.DB_PATH)

        # VARIABLE: Эмодзи для сообщений
        self.vl_em = "<:value_emoji:1553133311365349457>"
        self.ow_em = "<a:owner_emoji:1552781248236097546>"
        self.gr_em = "<a:alright_emoji:1552752070262521917>"
        self.mm_em = "<a:member_emoji:1553129529378078842>"
        self.at_em = "<a:attention_emoji:1552749665030508654>"

    # METHOD: Отправка сообщения с View
    async def send_message(self, destination: discord.Interaction, content: str, is_ephemeral=False):
        try:
            view = DefaultComponent(content)

            if isinstance(destination, discord.Interaction):
                if destination.response.is_done():
                    await destination.followup.send(
                        view=view,
                        ephemeral=is_ephemeral
                    )
                else:
                    await destination.response.send_message(
                        view=view,
                        ephemeral=is_ephemeral
                    )
                return

            await destination.send(
                view=view
            )
        except Exception as e:
            print(
                f"❌ Не удалось отправить сообщение пользователю: "
                f"{type(e).__name__}: {e}"
            )

    @app_commands.command(name="добавить_валюту", description="Добавить валюту пользователю.")
    @app_commands.describe(user="Пользователь.", points="Кол-во валюты.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    async def give(self, interaction: discord.Interaction, user: discord.User, points: int):
        channel = self.bot.get_channel(BotConfig.LOG_CHANNEL)
        user_data = await self.manager.get_user_economic(user.id)
        new_points = user_data["points"] + points
        await self.manager.update_user_economic(user.id, new_points, user_data["last_claim"], user_data["last_water"], user_data["last_collect"], user_data["last_fish"], user_data["last_bonus"], user_data["last_rob"])

        # LOGIC: Отправка в чат
        msg = (
            f"{self.mm_em} ᴨоᴧьзоʙᴀᴛᴇᴧю {user.mention} добᴀʙᴧᴇно {points} {self.vl_em}.\n"
            f"{self.mm_em} ноʙый бᴀᴧᴀнᴄ ᴨоᴧьзоʙᴀᴛᴇᴧя: {new_points} {self.vl_em}."
            f"\n\n-# {self.ow_em} ʙ ᴄᴧучᴀᴇ зᴧоуᴨоᴛᴩᴇбᴧᴇния — нᴀᴋᴀзᴀниᴇ."
            )
        await self.send_message(interaction, msg, True)

        # LOGIC: Отправка в логи
        l_msg = (
            f"### {self.mm_em} ʙыдᴀчᴀ ʙᴀᴧюᴛы.\n"
            f"{self.gr_em} ᴨоᴧьзоʙᴀᴛᴇᴧь {interaction.user.mention} ʙыдᴀᴧ иᴦᴩоᴋу {user.mention} ʙᴀᴧюᴛу\n"
            f"{self.gr_em} ᴩᴀзʍᴇᴩ ʙыдᴀнной ʙᴀᴧюᴛы: {points} {self.vl_em}\n\n"
            f"{self.at_em} ноʙый бᴀᴧᴀнᴄ ᴨоᴧьзоʙᴀᴛᴇᴧя: {new_points} {self.vl_em}"
            f"\n\n-# {self.ow_em} ʙ ᴄᴧучᴀᴇ зᴧоуᴨоᴛᴩᴇбᴧᴇния — ʙы ʙ ᴨᴩᴀʙᴇ нᴀᴋᴀзᴀᴛь ᴇᴦо."
            )
        await self.send_message(channel, l_msg)

    @app_commands.command(name="заморозить_валюту", description="Заморозить валюту у пользователя.")
    @app_commands.describe(user="Пользователь.", points="Кол-во валюты.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    async def take(self, interaction: discord.Interaction, user: discord.User, points: int):
        channel = self.bot.get_channel(BotConfig.LOG_CHANNEL)
        user_data = await self.manager.get_user_economic(user.id)
        new_points = max(0, user_data["points"] - points)
        await self.manager.update_user_economic(user.id, new_points, user_data["last_claim"], user_data["last_water"], user_data["last_collect"], user_data["last_fish"], user_data["last_bonus"], user_data["last_rob"])

        # LOGIC: Отправка в чат
        msg = (
            f"{self.mm_em} у ᴨоᴧьзоʙᴀᴛᴇᴧя {user.mention} зᴀбᴩᴀно {points} {self.vl_em}.\n"
            f"{self.mm_em} ноʙый бᴀᴧᴀнᴄ ᴨоᴧьзоʙᴀᴛᴇᴧя: {new_points} {self.vl_em}."
            f"\n\n-# {self.ow_em} ʙ ᴄᴧучᴀᴇ зᴧоуᴨоᴛᴩᴇбᴧᴇния — нᴀᴋᴀзᴀниᴇ."
            )
        await self.send_message(interaction, msg, True)

        # LOGIC: Отправка в логи
        l_msg = (
            f"### {self.mm_em} зᴀʍоᴩозᴋᴀ ʙᴀᴧюᴛы.\n"
            f"{self.gr_em} ᴨоᴧьзоʙᴀᴛᴇᴧь {interaction.user.mention} зᴀʍоᴩозиᴧ у иᴦᴩоᴋᴀ {user.mention} ʙᴀᴧюᴛу\n"
            f"{self.gr_em} ᴩᴀзʍᴇᴩ зᴀʍоᴩожᴇнной ʙᴀᴧюᴛы: {points} {self.vl_em}\n\n"
            f"{self.at_em} ноʙый бᴀᴧᴀнᴄ ᴨоᴧьзоʙᴀᴛᴇᴧя: {new_points} {self.vl_em}"
            f"\n\n-# {self.ow_em} ʙ ᴄᴧучᴀᴇ зᴧоуᴨоᴛᴩᴇбᴧᴇния — ʙы ʙ ᴨᴩᴀʙᴇ нᴀᴋᴀзᴀᴛь ᴇᴦо."
            )
        await self.send_message(channel, l_msg)

    # Включить/выключить все транкзации через boolean переменную

    # Админ панелька с кнопками для быстрого взъимания и добавления валюты

# LOGIC: Запуск кога
async def setup(bot):
    await bot.add_cog(AdminCog(bot))