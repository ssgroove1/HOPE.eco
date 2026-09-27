import discord
from discord import app_commands
from pathlib import Path
from discord.ext import commands

# Импорт ваших собственных настроек и функций из корня проекта
from config import BotConfig
from database.db_logic import DB_Manager

# Корень проекта (поднимаемся из папки cogs/ на один уровень вверх)
BASE_DIR = Path(__file__).resolve().parent.parent

# COMPANENT: Компанент лидерборда
class LeaderboardComponent(discord.ui.LayoutView):
    def __init__(self, guild, leaderboard):
        super().__init__(timeout=None)

        # VARIABLE: Эмодзи для сообщений
        ow_em = "<a:owner_emoji:1552781248236097546>"
        gm_em = "<a:star_emoji:1553416240142360627>"

        self.InfoContainer = discord.ui.Container(
            discord.ui.TextDisplay(
                content=(
                    f"## ᴧидᴇᴩбоᴩд ᴄᴇᴩʙᴇᴩᴀ {gm_em}\n"
                    f"-# Это информация о лидерборде сервера, **{guild.name}**, "
                    "здесь вы можете получить полезную информацию о количестве валюты пользователей."
                ),
            ),

            discord.ui.Separator(
                visible=True,
                spacing=discord.SeparatorSpacing.large,
            ),

            discord.ui.TextDisplay(
                content=leaderboard,
            ),

            discord.ui.Separator(
                visible=True,
                spacing=discord.SeparatorSpacing.large,
            ),

            discord.ui.TextDisplay(
                content=(
                    f"-# Считаете это ошибочной информацией, сообщите создателю. {ow_em}"
                ),
            ),

            discord.ui.Separator(
                visible=True,
                spacing=discord.SeparatorSpacing.large,
            ),
        )

        self.add_item(self.InfoContainer)

# COMPANENT: Компанент баланса пользователя
class BalanceComponent(discord.ui.LayoutView):
    def __init__(self, user, points, container_count, leaderboard):
        super().__init__(timeout=None)

        avatar_url = user.display_avatar.url

        # VARIABLE: Эмодзи для сообщений
        vl_em = "<:value_emoji:1553133311365349457>"
        ow_em = "<a:owner_emoji:1552781248236097546>"
        mm_em = "<a:member_emoji:1553129529378078842>"
        sl_em = "<a:sheild_emoji:1553396505665085500>"
        ts_em = "<a:tombstone_emoji:1553765267979636766>"

        self.InfoContainer = discord.ui.Container(
            discord.ui.TextDisplay(
                content=(
                    f"## бᴀᴧᴀнᴄ ᴨоᴧьзоʙᴀᴛᴇᴧя {sl_em}\n"
                    f"-# Это информация о балансе пользователя, {user.mention}, здесь вы можете получить полезную информацию о количестве валюты пользователя."
                ),
            ),
            discord.ui.Separator(
                visible=True,
                spacing=discord.SeparatorSpacing.large,
            ),
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=(
                        f"- **ᴛᴇᴋущий бᴀᴧᴀнᴄ ᴨоᴧьзоʙᴀᴛᴇᴧя**: {points} {vl_em}\n"
                        f"- **ʍᴇᴄᴛо ʙ ᴛᴀбᴧицᴇ ᴧидᴇᴩоʙ**: {leaderboard} {mm_em}\n"
                        f"- **оᴛᴋᴩыᴛых ᴋонᴛᴇйнᴇᴩоʙ**: {container_count} {ts_em}"
                    ),
                ),
                    accessory=discord.ui.Thumbnail(
                        avatar_url,
                ),
            ),
            discord.ui.Separator(
                visible=True,
                spacing=discord.SeparatorSpacing.large,
            ),
            discord.ui.TextDisplay(
                content=(
                    f"-# Считаете это ошибочной информацией, сообщите создателю. {ow_em}"
                ),
            ),
            discord.ui.Separator(
                visible=True,
                spacing=discord.SeparatorSpacing.large,
            ),
        )

        self.add_item(self.InfoContainer)

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

# LOGIC: Основной функционал информационных ф-ций
class InformationCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.manager = DB_Manager(BotConfig.DB_PATH)

        # VARIABLE: Эмодзи для сообщений
        self.vl_em = "<:value_emoji:1553133311365349457>"
        self.ow_em = "<a:owner_emoji:1552781248236097546>"
        self.gr_em = "<a:alright_emoji:1552752070262521917>"
        self.mm_em = "<a:member_emoji:1553129529378078842>"
        self.dn_em = "<a:denied_emoji:1552780290609512658>"
        self.gm_em = "<a:star_emoji:1553416240142360627>"

    # METHOD: Отправка сообщения с View
    async def send_message(self, destination: discord.Interaction, content: str, is_ephemeral=False):
        try:
            view = DefaultComponent(content)

            if destination.response.is_done():
                await destination.followup.send(
                    view=view,
                    ephemeral=is_ephemeral,
                    allowed_mentions=discord.AllowedMentions.none()
                )
            else:
                await destination.response.send_message(
                    view=view,
                    ephemeral=is_ephemeral,
                    allowed_mentions=discord.AllowedMentions.none()
                )
            return

        except Exception as e:
            print(
                f"❌ Не удалось отправить сообщение пользователю: "
                f"{type(e).__name__}: {e}"
            )

    @app_commands.command(name="баланс", description="Посмотреть баланс.")
    @app_commands.describe(member="Валюта пользователя (не обяз. вводить).")
    @app_commands.guild_only()
    async def balance(self, interaction: discord.Interaction, member: discord.Member = None):
        if interaction.channel.id != BotConfig.COMMAND_CHANNEL:
            await self.send_message(interaction,
                (
                    f"{self.dn_em} ϶ᴛᴀ ᴋоʍᴀндᴀ ᴩᴀбоᴛᴀᴇᴛ ᴛоᴧьᴋо ʙ ᴋᴀнᴀᴧᴇ <#{BotConfig.COMMAND_CHANNEL}>!\n"
                    f"\n-# {self.ow_em} ᴨожᴀᴧуйᴄᴛᴀ, ʙʙодиᴛᴇ ᴋоʍᴀнды ʙ оᴄобоʍ ᴋᴀнᴀᴧᴇ."
                )
            , True)
            return
        if member is None:
            member = interaction.user
        user_data = await self.manager.get_user_economic(member.id)
        if user_data is None:
            print("Нет данных о пользователе")
            return

        rank = self.manager.get_user_rank(member.id)
        if rank is None:
            leaderboard_status = "оᴛᴄуᴛᴄᴛʙуᴇᴛ."
        else:
            leaderboard_status = rank

        try:
            view = BalanceComponent(member, user_data["points"], user_data["container_count"], leaderboard_status)
        except Exception as e:
            print(f"❌ BalanceComponent: {type(e).__name__}: {e}")
            raise

        if interaction.response.is_done():
            await interaction.followup.send(view=view, ephemeral=False, allowed_mentions=discord.AllowedMentions.none())
        else:
            await interaction.response.send_message(view=view, ephemeral=False, allowed_mentions=discord.AllowedMentions.none())

    @app_commands.command(name="лидерборд", description="Показывает лидерборд игроков.")
    @app_commands.guild_only()
    async def top_players(self, interaction: discord.Interaction):
        if interaction.channel.id != BotConfig.COMMAND_CHANNEL:
            await self.send_message(interaction,
                (
                    f"{self.dn_em} ϶ᴛᴀ ᴋоʍᴀндᴀ ᴩᴀбоᴛᴀᴇᴛ ᴛоᴧьᴋо ʙ ᴋᴀнᴀᴧᴇ <#{BotConfig.COMMAND_CHANNEL}>!\n"
                    f"\n-# {self.ow_em} ᴨожᴀᴧуйᴄᴛᴀ, ʙʙодиᴛᴇ ᴋоʍᴀнды ʙ оᴄобоʍ ᴋᴀнᴀᴧᴇ."
                )
            , True)
            return

        rows = self.manager.get_leaderboard()
        if not rows:
            await self.send_message(interaction, f"{self.gm_em} ᴨоᴋᴀ нᴇᴛ иᴦᴩоᴋоʙ ᴄ очᴋᴀʍи!\n\n-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю.", True)
            return

        leaderboard_text = ""
        for i, row in enumerate(rows, 1):

            user_id = row[0]
            points = row[1]

            user = interaction.guild.get_member(user_id)

            if user:
                name = user.mention
            else:
                name = f"<@{user_id}>"

            medal = ""

            if i == 1:
                medal = "<a:top1_emoji:1553415275070890035> "
            elif i == 2:
                medal = "<a:top2_emoji:1553415533444206753> "
            elif i == 3:
                medal = "<a:top3_emoji:1553415532143714514> "
            else:
                medal = "<:inf_emoji:1553417868110991440> "

            leaderboard_text += (
                f"{medal}`#{i}` **{name}** — "
                f"`{points}` {self.vl_em}\n"
            )

        try:
            view = LeaderboardComponent(interaction.guild, leaderboard_text)
        except Exception as e:
            print(f"❌ BalanceComponent: {type(e).__name__}: {e}")
            raise
        
        if interaction.response.is_done():
            await interaction.followup.send(view=view, ephemeral=False, allowed_mentions=discord.AllowedMentions.none())
        else:
            await interaction.response.send_message(view=view, ephemeral=False, allowed_mentions=discord.AllowedMentions.none())

    # Быстрые действия

    # Магазин

# LOGIC: Запуск кога
async def setup(bot):
    await bot.add_cog(InformationCog(bot))