import discord, time, random, sqlite3
from discord import app_commands
from pathlib import Path
from discord.ext import commands, tasks
from collections import Counter

# Импорт ваших собственных настроек и функций из корня проекта
from config import BotConfig
from database.db_logic import DB_Manager

# LOGIC: Модуль кол-во валюты
class BetModal(discord.ui.Modal, title="Поставить ставку"):
    amount = discord.ui.TextInput(
        label="Количество валюты",
        placeholder="Введите сумму ставки...",
        min_length=2,
        max_length=15,
        required=True,
    )

    def __init__(self, cog, view):
        super().__init__(timeout=120)
        self.cog = cog
        self.casino_view = view

    async def on_submit(self, interaction: discord.Interaction):
        view = self.casino_view
        user_id = interaction.user.id
        
        if user_id != view.owner_id:
            content = (
                f"{self.cog.dn_em} ᴨоᴧьзоʙᴀᴛᴇᴧь, {interaction.user.mention}, ϶ᴛо нᴇ ʙᴀɯᴀ ʍᴀɯинᴀ!\n"
                f"{self.cog.dn_em} ʙʙᴇдиᴛᴇ ᴋоʍᴀнду /казино дᴧя ᴄʙоᴇй ʍᴀɯины.\n\n"
                f"-# {self.cog.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
            )
            await self.cog.send_message(
                interaction, content, True
            )
            return

        try:
            amount = int(self.amount.value.strip())
        except ValueError:
            content = (
                f"{self.cog.dn_em} ʙʙᴇдиᴛᴇ ᴄуʍʍу циɸᴩᴀʍи, нᴇ иᴄᴨоᴧьзуйᴛᴇ дᴩуᴦиᴇ ᴄиʍʙоᴧы.\n"
                f"{self.cog.dn_em} ᴨоᴨᴩобуйᴛᴇ ᴄноʙᴀ, иᴄᴨоᴧьзуя циɸᴩы.\n\n"
                f"-# {self.cog.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
            )
            await self.cog.send_message(
                interaction, content, True,
            )
            return

        if amount <= 0:
            content = (
                f"{self.cog.dn_em} сумма должна быть больше нуля.\n"
                f"{self.cog.dn_em} ᴨоᴨᴩобуйᴛᴇ ᴄноʙᴀ.\n\n"
                f"-# {self.cog.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
            )
            await self.cog.send_message(
                interaction, content, True
            )
            return

        balance = await self.cog.manager.get_user_points(user_id)

        if amount > balance:
            content = (
                f"{self.cog.dn_em} у ʙᴀᴄ нᴇдоᴄᴛᴀᴛочно ᴄᴩᴇдᴄᴛʙ нᴀ ᴄчᴇᴛу.\n"
                f"{self.cog.dn_em} ʙᴀɯ ᴛᴇᴋущий бᴀᴧᴀнᴄ: {balance} {self.cog.vl_em}.\n\n"
                f"-# {self.cog.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
            )
            await self.cog.send_message(
                interaction, content, True
            )
            return

        await interaction.response.defer(ephemeral=True, thinking=True)

        try:
            result = await self.cog.play_slots(interaction.user, balance, amount)

        except Exception as e:
            print("ОШИБКА:", repr(e))

            content = (
                f"{self.cog.dn_em} нᴇ удᴀᴧоᴄь обᴩᴀбоᴛᴀᴛь ᴨоᴨыᴛᴋу.\n"
                f"{self.cog.dn_em} ᴨоᴨᴩобуйᴛᴇ ᴨозжᴇ.\n\n"
                f"-# {self.cog.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю.")

            await self.cog.send_message(destination=interaction, content=content)
            raise

        await self.cog.manager.add_points(user_id, result["value"])

        await self.cog.send_message(
            interaction, result["text"]
        )

# COMPANENT: Компанент простого текстового сообщения
class DefaultComponent(discord.ui.LayoutView):
    def __init__(
        self,
        content,
    ):
        super().__init__()

        # LOGIC: Создаем контейнер с текстовым сообщением
        self.InfoContainer = discord.ui.Container(
            discord.ui.TextDisplay(content=content),
        )
        self.add_item(self.InfoContainer)

# COMPANENT: Компанент машины слотов
class CasinoComponent(discord.ui.LayoutView):
    def __init__(self, cog, user):
        super().__init__(timeout=300)

        self.cog = cog
        self.owner_id = user.id
        self.message = None

        self.bet_button = discord.ui.Button(
            style=discord.ButtonStyle.success,
            label="ᴨоᴄᴛᴀʙиᴛь ᴄᴛᴀʙᴋу",
            emoji=discord.PartialEmoji(
                name="alright_emoji",
                id=1552752070262521917,
                animated=True,
            ),
            custom_id="btn_action",
        )

        self.break_button = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="ᴄᴧоʍᴀᴛь ʍᴀɯину",
            emoji=discord.PartialEmoji(
                name="denied_emoji",
                id=1552780290609512658,
                animated=True,
            ),
            custom_id="btn_action_2",
        )

        self.bet_button.callback = self.on_bet
        self.break_button.callback = self.on_break_button

        self.add_item(
            discord.ui.Container(
                discord.ui.TextDisplay(
                    f"# ᴋᴀзино ʍᴀɯинᴀ {self.cog.sm_em}"
                ),
                discord.ui.TextDisplay(
                    f"-# ʍᴀɯинᴀ ᴄо ᴄᴧоᴛᴀʍ ᴨоᴧьзоʙᴀᴛᴇᴧя {user.mention}, "
                    f"иᴄᴨоᴧьзующᴀя ʙᴄю ʙᴀɯу жизнᴇнную ᴄиᴧу и дуɯу, "
                    f"ᴨᴩᴇʙᴩᴀщᴀя ϶ᴛо ʙ ʙᴀᴧюᴛу ᴄᴇᴩʙᴇᴩᴀ."
                ),
                discord.ui.Separator(
                    visible=True,
                    spacing=discord.SeparatorSpacing.small,
                ),
                discord.ui.TextDisplay(
                    f"### ᴀʙᴛоʍᴀᴛ ᴛᴀᴋ и жᴀждᴇᴛ ʙᴀɯих дᴇйᴄᴛʙий {self.cog.at_em}\n"
                    "- поставить ставку в размере ... ?\n"
                    "- бросить автомат в одиночестве?\n"
                    f"### ʙозьʍиᴛᴇ ᴄ ᴄобой ᴨодᴋоʙу дᴧя удᴀчи {self.cog.at_em}"
                ),
                discord.ui.Separator(
                    visible=True,
                    spacing=discord.SeparatorSpacing.small,
                ),
                discord.ui.ActionRow(
                    self.bet_button,
                    self.break_button,
                ),
            )
        )

    async def interaction_check(self, interaction):
        if interaction.user.id != self.owner_id:
            await self.cog.send_message(interaction, (
                f"{self.cog.dn_em} ᴨоᴧьзоʙᴀᴛᴇᴧь, {interaction.user.mention}, ϶ᴛо нᴇ ʙᴀɯᴀ ʍᴀɯинᴀ!\n"
                f"{self.cog.dn_em} ʙʙᴇдиᴛᴇ ᴋоʍᴀнду /казино дᴧя ᴄʙоᴇй ʍᴀɯины.\n\n"
                f"-# {self.cog.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
            ), True)
            return False
        return True

    async def on_bet(self, interaction: discord.Interaction):
        await interaction.response.send_modal(BetModal(cog=self.cog, view=self))

    async def on_break_button(
        self,
        interaction: discord.Interaction,
    ):
        try:
            content = (
                f"{self.cog.dn_em} ʍᴀɯинᴀ ᴨоʙᴩᴇждᴇнᴀ, дᴀᴧьнᴇйɯᴀя ᴩᴀбоᴛᴀ нᴇʙозʍожнᴀ.\n"
                f"{self.cog.dn_em} ʙʙᴇдиᴛᴇ ᴋоʍᴀнду /казино дᴧя ᴄʙоᴇй ʍᴀɯины.\n\n"
                f"-# {self.cog.ow_em} ᴄообщᴇниᴇ быᴧᴏ удᴀᴧᴇно "
                f"из-зᴀ ᴨоᴧьзоʙᴀᴛᴇᴧя."
            )

            view = DefaultComponent(content=content)

            await self.message.edit(
                view=view
            )

        except discord.NotFound:
            pass

        except discord.HTTPException as error:
            print(
                f"❌ Ошибка при timeout: "
                f"{type(error).__name__}: {error}"
            )

        self.stop()

    # METHOD: Обработка таймаута
    async def on_timeout(self):
        for item in self.walk_children():
            if isinstance(item, discord.ui.Select):
                item.disabled = True
        if self.message is None:
            return
        try:
            content = (
                f"ᴄᴧоᴛ ʍᴀɯину нᴀᴋᴩыᴧи, дᴀᴧьнᴇйɯᴀя ᴩᴀбоᴛᴀ нᴇʙозʍожнᴀ.\n"
                f"{self.cog.dn_em} ʙʙᴇдиᴛᴇ ᴋоʍᴀнду /казино дᴧя ᴄʙоᴇй ʍᴀɯины.\n\n"
                f"-# {self.cog.ow_em} ᴄообщᴇниᴇ быᴧᴏ удᴀᴧᴇно "
                f"из-зᴀ ᴛᴀйʍᴀуᴛᴀ (5 ʍинуᴛ)."
            )

            view = DefaultComponent(content=content)

            await self.message.edit(
                view=view
            )

        except discord.NotFound:
            pass

        except discord.HTTPException as error:
            print(
                f"❌ Ошибка при timeout: "
                f"{type(error).__name__}: {error}"
            )

# LOGIC: Основной функционал обработки казино
class CasinoCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.manager = DB_Manager(BotConfig.DB_PATH)

        # VARIABLE: Эмодзи для сообщений
        self.sm_em = "<a:slot_emoji:1559246672427749518>"
        self.vl_em = "<:value_emoji:1553133311365349457>"
        self.dn_em = "<a:denied_emoji:1552780290609512658>"
        self.gr_em = "<a:alright_emoji:1552752070262521917>"
        self.wt_em = "<a:wait_emoji:1552785236549443634>"
        self.ow_em = "<a:owner_emoji:1552781248236097546>"
        self.sp_em = "<a:shop_emoji:1554944276625105026>"
        self.at_em = "<a:attention_emoji:1552749665030508654>"
        self.cl_em = "<a:cult_emoji:1553433613012566066>"

        # VARIABLE: Эмодзи для казино
        self.slot1 = "<a:slot1_emoji:1563296464216784897>"
        self.slot2 = "<a:slot2_emoji:1563296467135766669>"
        self.slot3 = "<a:slot3_emoji:1563296469740556399>"
        self.slot4 = "<a:slot4_emoji:1563296473054052392>"
        self.slot5 = "<a:slot5_emoji:1563296476224946186>"

    # METHOD: Отправка сообщения с View
    async def send_message(self, destination: discord.Interaction | discord.abc.Messageable, content: str, is_ephemeral=False):
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

    # METHOD: Проверка на отправку сообщения
    async def command_checks(self, interaction: discord.Interaction) -> bool:
        if interaction.channel.id != BotConfig.COMMAND_CHANNEL:
            msg = (
                f"{self.dn_em} ϶ᴛᴀ ᴋоʍᴀндᴀ ᴩᴀбоᴛᴀᴇᴛ ᴛоᴧьᴋо ʙ ᴋᴀнᴀᴧᴇ <#{BotConfig.COMMAND_CHANNEL}>!\n"
                f"\n-# {self.ow_em} ᴨожᴀᴧуйᴄᴛᴀ, ʙʙодиᴛᴇ ᴋоʍᴀнды ʙ оᴄобоʍ ᴋᴀнᴀᴧᴇ."
            )
            await self.send_message(interaction,
                msg
            , True)
            return False

        if not BotConfig.TRANSACTIONS_AVAILABLE:
            msg = (
                f"{self.dn_em} ʙ дᴀнный ʍоʍᴇнᴛ ᴋоʍᴀндᴀ нᴇ доᴄᴛуᴨнᴀ.\n{self.dn_em} циᴩᴋуᴧяция ʙᴀᴧюᴛы ʙᴩᴇʍᴇнно оᴄᴛᴀноʙᴧᴇнᴀ."
                f"\n\n-# {self.ow_em} ᴨᴩиноᴄиʍ изʙинᴇния зᴀ нᴇудобᴄᴛʙᴀ, ᴨᴩобᴧᴇʍᴀ ᴩᴇɯᴀᴇᴛᴄя."
            )
            await self.send_message(interaction,
                msg
            , True)
            return False

        bot_member = interaction.guild.me
        if bot_member is None:
            msg = (
                f"{self.dn_em} нᴇ удᴀᴧоᴄь ᴨоᴧучить дᴀнныᴇ бoᴛᴀ нᴀ ᴄᴇᴩʙᴇᴩᴇ."
                f"\n\n-# {self.ow_em} ᴄоздᴀᴛᴇᴧь боᴛᴀ оᴄʙᴇдоʍᴧᴇн об ϶ᴛоʍ."
            )
            await self.send_message(
                interaction,
                msg,
                True
            )
            return False

        return True

    # LOGIC: Игра в слоты
    async def play_slots(self, user, user_balance, bet: int) -> dict:
        if bet <= 0:
            raise ValueError("Ставка должна быть больше нуля.")

        symbols = {
            self.slot1: 2,
            self.slot2: 2.2,
            self.slot3: 2.4,
            self.slot4: 2.6,
            self.slot5: 2.8,
        }

        reels = random.choices(
            list(symbols.keys()),
            k=3,
        )

        result_text = None
        value = 0
        multiplier = 0

        counts = Counter(reels)
        if 3 in counts.values():
            multiplier = symbols[reels[0]]
            value = bet * multiplier

            balance = int(user_balance + value)

            result_text = (
                f"## ᴊᴀᴄᴋᴘᴏᴛ {self.sm_em}\n"
                f"{user.mention}, — {' | '.join(reels)}\n\n"
                f"{self.gr_em} ʍножиᴛᴇᴧь ʙᴀᴧюᴛы: x{multiplier}\n"
                f"{self.gr_em} ваш выйгрыш: {value} {self.vl_em}\n"
                f"{self.gr_em} ᴛᴇᴋущий бᴀᴧᴀнᴄ: {balance} {self.vl_em}"
                f"\n\n-# {self.cl_em} ᴋуᴧьᴛ ᴦоᴩдиᴛᴄя ʙᴀʍи, нᴇ оᴄᴛᴀʙᴧяйᴛᴇ ᴇᴦо, ᴀ он — ʙᴀᴄ."
            )

        elif 2 in counts.values():
            value = 0

            result_text = (
                f"## sᴀᴠᴇᴅ ʙᴇᴛ {self.sm_em}\n"
                f"{user.mention}, — {' | '.join(reels)}\n\n"
                f"{self.gr_em} ʙᴀɯᴀ ᴄᴛᴀʙᴋᴀ ᴄохᴩᴀнᴇнᴀ...\n"
                f"{self.gr_em} ᴛᴇᴋущий бᴀᴧᴀнᴄ: {user_balance} {self.vl_em}"
                f"\n\n-# {self.cl_em} ᴋуᴧьᴛ ᴦоᴩдиᴛᴄя ʙᴀʍи, нᴇ оᴄᴛᴀʙᴧяйᴛᴇ ᴇᴦо, ᴀ он — ʙᴀᴄ."
            )

        else:
            value = -bet

            balance = int(user_balance - bet)

            result_text = (
                f"## ʟᴏsᴇʀ ʙᴇᴛ {self.sm_em}\n"
                f"{user.mention}, — {' | '.join(reels)}\n\n"
                f"{self.dn_em} ᴩᴀзʍᴇᴩ ᴨᴩоиᴦᴩᴀнной ᴄᴛᴀʙᴋи: {bet} {self.vl_em}\n"
                f"{self.dn_em} ᴛᴇᴋущий бᴀᴧᴀнᴄ: {balance} {self.vl_em}"
                f"\n\n-# {self.cl_em} ᴋуᴧьᴛ нᴀдᴇяᴛьᴄя нᴀ ʙᴀᴄ, нᴇ оᴄᴛᴀʙᴧяйᴛᴇ ᴇᴦо, ᴀ он — ʙᴀᴄ."
            )
        return {
            "value": value,
            "text": result_text
        }

    # COMMAND: Вызов машины слотов
    @app_commands.command(name="казино", description="Вызвать машину слотов.")
    @app_commands.guild_only()
    async def casino_command(self, interaction: discord.Interaction):
        try:
            view = CasinoComponent(
                cog=self,
                user=interaction.user
            )

            await interaction.response.send_message(view=view)

            view.message = await interaction.original_response()

        except Exception as e:
            print(
                f"❌ Не удалось отправить сообщение пользователю: "
                f"{type(e).__name__}: {e}"
            )

# LOGIC: Запуск кога
async def setup(bot):
    await bot.add_cog(CasinoCog(bot))