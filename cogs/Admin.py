import discord
from discord import app_commands
from pathlib import Path
from discord.ext import commands

# Импорт ваших собственных настроек и функций из корня проекта
from config import BotConfig
from database.db_logic import DB_Manager

# Корень проекта (поднимаемся из папки cogs/ на один уровень вверх)
BASE_DIR = Path(__file__).resolve().parent.parent

# COMPANENT: Компанент подверждения действия
class ConfirmComponent(discord.ui.LayoutView):
    def __init__(
        self,
        on_confirm = None
    ):
        super().__init__(timeout=60)

        self.message = None
        self.on_confirm = on_confirm

        # VARIABLE: Эмодзи для сообщений
        ow_em = "<a:owner_emoji:1552781248236097546>"
        at_em = "<a:attention_emoji:1552749665030508654>"

        self.confirm_button = discord.ui.Button(
            style=discord.ButtonStyle.success,
            label="ᴨодʙᴇᴩждᴀᴇᴛᴇ ᴧи ʙы ᴄʙои дᴇйᴄᴛʙия?",
            emoji=discord.PartialEmoji(
                name="alright_emoji",
                id=1552752070262521917,
                animated=True
            ),
            custom_id="btn_action",
        )

        self.cancel_button = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="оᴛʍᴇниᴛь ᴄʙои дᴇйᴄᴛʙия.",
            emoji=discord.PartialEmoji(
                name="denied_emoji",
                id=1552780290609512658,
                animated=True
            ),
            custom_id="btn_action_2",
        )

        # Callback кнопок
        self.confirm_button.callback = self.confirm
        self.cancel_button.callback = self.cancel

        self.InfoContainer = discord.ui.Container(
            discord.ui.TextDisplay(
                content=(
                    f"{at_em} ᴦоᴛоʙы ᴧи ʙы ʙзяᴛь оᴛʙᴇᴛᴄᴛʙᴇнноᴄᴛь зᴀ ϶ᴛо дᴇйᴄᴛʙиᴇ?\n"
                    f"{at_em} обᴩᴀᴛиᴛь ϶ᴛо дᴇйᴄᴛʙиᴇ ужᴇ нᴇᴧьзя будᴇᴛ.\n"
                    f"{at_em} будᴇᴛ оᴛᴋᴧонᴇно ᴨоᴄᴧᴇ 60 ᴄᴇᴋунд бᴇздᴇйᴄᴛʙия.\n"
                    f"\n-# {ow_em} ʙ ᴄᴧучᴀᴇ зᴧоуᴨоᴛᴩᴇбᴧᴇния — нᴀᴋᴀзᴀниᴇ."
                ),
            ),
        )

        self.add_item(self.InfoContainer)

        self.add_item(
            discord.ui.ActionRow(
                self.confirm_button,
                self.cancel_button,
            ),
        )

    async def disable_buttons(self):
        self.confirm_button.disabled = True
        self.cancel_button.disabled = True

    async def confirm(self, interaction: discord.Interaction):
        await self.disable_buttons()

        await interaction.response.edit_message(view=self)

        await self.on_confirm(interaction)

        self.stop()

    async def cancel(self, interaction: discord.Interaction):
        await self.disable_buttons()

        await interaction.response.edit_message(view=self)

        self.stop()

    async def on_timeout(self):
        await self.disable_buttons()

        if self.message:
            await self.message.edit(
                view=self
            )

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
        self.dn_em = "<a:denied_emoji:1552780290609512658>"
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

    # METHOD: Выдачи/забирания валюты
    async def action_currency(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        points: int,
        reason: str,
        action: None
    ):
        action1 = ""
        action2 = ""
        action3 = ""
        action4 = ""
        if action == "take":
            action1 = "зᴀʍоᴩожᴇно"
            action2 = "зᴀʍоᴩозᴋᴀ"
            action3 = "зᴀʍоᴩожᴇнной"
            action4 = "зᴀʍоᴩозиᴧ"
        else:
            action1 = "добᴀʙᴧᴇно"
            action2 = "ʙыдᴀчᴀ"
            action3 = "ʙыдᴀнной"
            action4 = "ʙыдᴀᴧ"
        
        channel = self.bot.get_channel(BotConfig.LOG_CHANNEL)

        user_data = await self.manager.get_user_economic(user.id)

        new_points = None
        if action == "take":
            new_points = max(0, int(user_data["points"]) - points)
        else:
            new_points = int(user_data["points"] + points)

        await self.manager.update_user_economic(
            user.id,
            new_points,
            user_data["last_claim"],
            user_data["last_water"],
            user_data["last_collect"],
            user_data["last_fish"],
            user_data["last_bonus"],
            user_data["last_rob"]
        )

        # LOGIC: Отправка в чат
        msg = (
            f"{self.mm_em} ᴨоᴧьзоʙᴀᴛᴇᴧю {user.mention} {action1} {points} {self.vl_em}.\n"
            f"{self.mm_em} ноʙый бᴀᴧᴀнᴄ ᴨоᴧьзоʙᴀᴛᴇᴧя: {new_points} {self.vl_em}."
            f"\n\n-# {self.ow_em} ʙ ᴄᴧучᴀᴇ зᴧоуᴨоᴛᴩᴇбᴧᴇния — нᴀᴋᴀзᴀниᴇ."
            )
        await self.send_message(interaction, msg, True)

        # LOGIC: Отправка в логи
        l_msg = (
            f"### {self.mm_em} {action2} ʙᴀᴧюᴛы.\n"
            f"{self.gr_em} ᴨоᴧьзоʙᴀᴛᴇᴧь {interaction.user.mention} {action4} иᴦᴩоᴋу {user.mention} ʙᴀᴧюᴛу\n"
            f"{self.gr_em} ᴩᴀзʍᴇᴩ {action3} ʙᴀᴧюᴛы: {points} {self.vl_em}\n\n"
            f"{self.at_em} ᴨᴩичинᴀ: {reason}\n"
            f"{self.at_em} ноʙый бᴀᴧᴀнᴄ ᴨоᴧьзоʙᴀᴛᴇᴧя: {new_points} {self.vl_em}"
            f"\n\n-# {self.ow_em} ʙ ᴄᴧучᴀᴇ зᴧоуᴨоᴛᴩᴇбᴧᴇния — ʙы ʙ ᴨᴩᴀʙᴇ нᴀᴋᴀзᴀᴛь ᴇᴦо."
            )
        await self.send_message(channel, l_msg)

    @app_commands.command(name="добавить_валюту", description="Добавить валюту пользователю.")
    @app_commands.describe(user="Пользователь.", points="Кол-во валюты.", reason="Укажите причину.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    async def give(self, interaction: discord.Interaction, user: discord.User, points: int, reason: str):
        async def confirm_action(confirm_interaction: discord.Interaction):
            await self.action_currency(
                confirm_interaction,
                user,
                points,
                reason,
                "give"
            )

        view = ConfirmComponent(
            on_confirm=confirm_action
        )

        await interaction.response.send_message(
            view=view,
            ephemeral=True
        )

        view.message = await interaction.original_response()

    @app_commands.command(name="заморозить_валюту", description="Заморозить валюту у пользователя.")
    @app_commands.describe(user="Пользователь.", points="Кол-во валюты.", reason="Укажите причину.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    async def take(self, interaction: discord.Interaction, user: discord.User, points: int, reason: str):
        async def confirm_action(confirm_interaction: discord.Interaction):
            await self.action_currency(
                confirm_interaction,
                user,
                points,
                reason,
                "take"
            )

        view = ConfirmComponent(
            on_confirm=confirm_action
        )

        await interaction.response.send_message(
            view=view,
            ephemeral=True
        )

        view.message = await interaction.original_response()

    # @app_commands.command(name="админ_панель", description="Быстрые действия с экономикой игрока.")
    # @app_commands.describe(user = "Действия направленные на это пользователя.")
    # @app_commands.guild_only()
    # @app_commands.checks.has_permissions(administrator=True)
    # async def panel(self, interaction: discord.Interaction, user: discord.User):
    #     pass

    @app_commands.command(name="регулирование_валют", description="Прекратить циркуляцию валюты внутри сервера.")
    @app_commands.describe(action="Включить (True), Выключить (False).", reason="Причина регулировки валюты?")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    async def regulator(self, interaction: discord.Interaction, reason: str, action: bool = BotConfig.TRANSACTIONS_AVAILABLE):
        async def confirm_action(confirm_interaction: discord.Interaction):
            action_text = ""
            action2_text = ""
            emoji = ""
            if action or BotConfig.TRANSACTIONS_AVAILABLE:
                action_text = "оᴄᴛᴀноʙᴧᴇн"
                action2_text = "оᴄᴛᴀноʙиᴧ"
                emoji = self.dn_em
                BotConfig.TRANSACTIONS_AVAILABLE = False
            else:
                action_text = "ʙоᴄᴄᴛᴀноʙᴧᴇн"
                action2_text = "ʙоᴄᴄᴛᴀноʙиᴧ"
                emoji = self.gr_em
                BotConfig.TRANSACTIONS_AVAILABLE = True

            channel = self.bot.get_channel(BotConfig.LOG_CHANNEL)

            content = (
                f"{emoji} циᴩᴋуᴧяция {action_text}ᴀ.\n"
                f"{emoji} ʙᴄᴇ ʙᴀᴧюᴛныᴇ ᴛᴩᴀнᴋзᴀᴋции {action_text}ы!"
                f"\n\n-# {self.ow_em} иᴄᴨоᴧьзуйᴛᴇ ϶ᴛу ᴋоʍᴀнду ʙ ᴛᴩудныᴇ ʍоʍᴇнᴛы. (нᴀᴋᴀзуᴇʍо)"
            )
            await self.send_message(confirm_interaction, content, True)

            l_msg = (
                f"### {emoji} {action_text}иᴇ циᴩᴋуᴧяции\n"
                f"{self.at_em} ᴨоᴧьзоʙᴀᴛᴇᴧь {interaction.user.mention} {action2_text} циᴩᴋуᴧяцию ʙᴀᴧюᴛы\n"
                f"{self.at_em} ᴨᴩичинᴀ дᴇйᴄᴛʙия: {reason}"
                f"\n\n-# {self.ow_em} ʙ ᴄᴧучᴀᴇ зᴧоуᴨоᴛᴩᴇбᴧᴇния — ʙы ʙ ᴨᴩᴀʙᴇ нᴀᴋᴀзᴀᴛь ᴇᴦо."
                )
            await self.send_message(channel, l_msg)

        view = ConfirmComponent(
            on_confirm=confirm_action
        )

        await interaction.response.send_message(
            view=view,
            ephemeral=True
        )

        view.message = await interaction.original_response()
    

# LOGIC: Запуск кога
async def setup(bot):
    await bot.add_cog(AdminCog(bot))