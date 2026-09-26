import discord
from discord import app_commands
from discord.ext import commands

from config import BotConfig

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

# LOGIC: Основной функционал экономических ф-ций
class SychronizationCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # VARIABLE: Эмодзи для сообщений
        self.at_em = "<a:attention_emoji:1552749665030508654>"
        self.ow_em = "<a:owner_emoji:1552781248236097546>"
        self.gr_em = "<a:alright_emoji:1552752070262521917>"

    # METHOD: Отправка сообщения с View
    async def send_message(self, interaction: discord.Interaction, view: discord.ui.View):
        try:
            if interaction.response.is_done():
                await interaction.followup.send(
                    view=view,
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(view=view, ephemeral=True)
        except Exception as e:
            print(
                f"❌ Не удалось отправить сообщение пользователю: "
                f"{type(e).__name__}: {e}"
            )

    # COMMAND: /unsync - удалить синхронизировать
    @app_commands.command(
        name="unsync",
        description="Рассинхронизировать команды."
    )
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def unsync(
        self,
        interaction: discord.Interaction
    ):
        msg = None
        if interaction.user.id != BotConfig.DEVELOPER_ID:
            sub_title = f"-# {self.ow_em} иᴄᴨоᴧьзуᴇᴛᴄя ᴛоᴧьᴋо ᴄоздᴀᴛᴇᴧᴇʍ, ᴋоᴦдᴀ ᴋоʍᴀнды боᴛᴀ бᴀᴩахᴧяᴛ."
            msg = f"{self.at_em} ᴋоʍᴀндa доᴄᴛуᴨнa ᴛоᴧьᴋo дᴧя ᴩᴀзᴩᴀбоᴛчиᴋa диᴄᴋoᴩд боᴛa.\n{self.at_em} ᴋoʍaндa ᴄоздaнa дᴧя ᴩaсcинхᴩонизaции ᴋoʍaнд боᴛa.\n\n{sub_title}"
        guild = interaction.guild
        if guild is None:
            msg = f"{self.at_em} ϶ᴛᴀ ᴋоʍᴀндa нeдоcтyпнa ʙ ᴧичных ᴄoобщeниях."

        if msg:
            view = DefaultComponent(msg)
            return await self.send_message(interaction, view)

        try:
            await interaction.response.defer(
                ephemeral=True
            )

            # Очищаем команды текущего сервера
            self.bot.tree.clear_commands(
                guild=guild
            )

            # Синхронизируем пустое дерево с Discord
            synced = await self.bot.tree.sync(
                guild=guild
            )

            sub_title = f"-# {self.ow_em} уᴄᴨᴇɯнᴀя ᴩᴇᴦиᴄᴛᴩᴀция ᴄоздᴀᴛᴇᴧя."
            msg = (
                f"{self.gr_em} ᴋоʍᴀнды удᴀᴧᴇны ᴄ ᴄᴇᴩʙᴇᴩᴀ `{guild.name}`.\n"
                f"{self.gr_em} оᴄᴛаᴧоᴄь ᴋоʍᴀнд: `{len(synced)}`"
                f"\n\n{sub_title}"
            )

            view = DefaultComponent(msg)

            await self.send_message(interaction, view)

        except discord.HTTPException as e:
            print(
                f"❌ [/unsync] Discord API: "
                f"{type(e).__name__}: {e}"
            )

            msg = f"{self.at_em} Discord API ʙᴇᴩнуᴧ оɯибᴋу:\n`{e}`"
            view = DefaultComponent(msg)

            await self.send_message(interaction, view)

    # COMMAND: /sync - синхронизировать
    @app_commands.command(
        name="sync",
        description="Синхронизировать команды.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    async def sync(self, interaction: discord.Interaction):
        msg = None
        if interaction.user.id != BotConfig.DEVELOPER_ID:
            sub_title = f"-# {self.ow_em} иᴄᴨоᴧьзуᴇᴛᴄя ᴛоᴧьᴋо ᴄоздᴀᴛᴇᴧᴇʍ, ᴋоᴦдᴀ ᴋоʍᴀнды боᴛᴀ бᴀᴩахᴧяᴛ."
            msg = f"{self.at_em} ᴋоʍᴀндa доcтyпнa тoᴧьᴋo дᴧя ᴩaзᴩaбоᴛчиᴋa диcкoᴩд боᴛa.\n{self.at_em} ᴋoʍaндa ᴄоздaнa дᴧя cинхᴩонизaции ᴋoʍaнд боᴛa.\n\n{sub_title}"
        guild = interaction.guild
        if guild is None:
            msg = f"{self.at_em} ϶ᴛᴀ ᴋоʍᴀндa нeдоcтyпнa ʙ ᴧичных ᴄoобщeниях."

        if msg:
            view = DefaultComponent(msg)
            return await self.send_message(interaction, view)

        try:
            await interaction.response.defer(ephemeral=True)

            # Берём глобальные команды и копируем их
            # в дерево этого сервера.
            self.bot.tree.copy_global_to(guild=guild)

            # Публикуем команды на сервере.
            synced = await self.bot.tree.sync(guild=guild)

            sub_title = f"-# {self.ow_em} уᴄᴨᴇɯнᴀя ᴩᴇᴦиᴄᴛᴩᴀция ᴄоздᴀᴛᴇᴧя."
            msg = (
                f"{self.gr_em} ᴋоʍᴀнды ᴄинхᴩонизиᴩоʙᴀны дᴧя ᴄᴇᴩʙᴇᴩᴀ `{guild.name}`.\n"
                f"{self.gr_em} ᴄинхᴩонизиᴩоʙᴀно: `{len(synced)}` ᴋоʍᴀнд"
                f"\n\n{sub_title}"
            )
            view = DefaultComponent(msg)

            await self.send_message(interaction, view)

        except discord.HTTPException as e:
            msg = f"{self.at_em} оɯибᴋᴀ Discord API: `{e}`"
            view = DefaultComponent(msg)

            await self.send_message(interaction, view)

            print(f"❌ Ошибка синхронизации команд на сервере {guild.name} (ID: {guild.id}): {e}")

# LOGIC: Запуск кога
async def setup(bot):
    await bot.add_cog(SychronizationCog(bot))