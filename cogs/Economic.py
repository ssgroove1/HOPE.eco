import discord, asyncio, time, random
from discord import app_commands
from pathlib import Path
from datetime import datetime
from discord.ext import commands

from config import BotConfig
from database.db_logic import DB_Manager

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

        # LOGIC: Callback кнопок
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

    # METHOD: Выключение/деактивация кнопок
    async def disable_buttons(self):
        self.confirm_button.disabled = True
        self.cancel_button.disabled = True

    # METHOD: Кнопка подверждения действия
    async def confirm(self, interaction: discord.Interaction):
        await self.disable_buttons()

        await interaction.response.edit_message(view=self)

        await self.on_confirm(interaction)

        self.stop()

    # METHOD: Кнопка отмены действия
    async def cancel(self, interaction: discord.Interaction):
        await self.disable_buttons()

        await interaction.response.edit_message(view=self)

        self.stop()

    # METHOD: Выключение/деактивация кнопок за время (60 секунд)
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

# LOGIC: Основной функционал экономических ф-ций
class EconomicCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.manager = DB_Manager(BotConfig.DB_PATH)

        # VARIABLE: Эмодзи для сообщений
        self.vl_em = "<:value_emoji:1553133311365349457>"
        self.gr_em = "<a:alright_emoji:1552752070262521917>"
        self.dn_em = "<a:denied_emoji:1552780290609512658>"
        self.wt_em = "<a:wait_emoji:1552785236549443634>"
        self.ow_em = "<a:owner_emoji:1552781248236097546>"
        self.cl_em = "<a:cult_emoji:1553433613012566066>"
        self.st_em = "<:shiny_emoji:1558391640295604345>"
        self.at_em = "<a:attention_emoji:1552749665030508654>"

        # LOGIC: Переменная для хранение данных рыб
        self.fish_info = {
            "common": {
                "ᴩубᴇц": {
                    "emoji": "<:common_fish:1558444884044681246>",
                    "rarity": "ɸизичᴇᴄᴋᴀя",
                    "chance": 65,
                    "price_from": 14,
                    "price_until": 23
                },
                "ᴄᴋᴀᴀз": {
                    "emoji": "<:uncommon_fish:1558444836468822036>",
                    "rarity": "духоʙнᴀя",
                    "chance": 35,
                    "price_from": 17,
                    "price_until": 28
                }
            },
            "epic": {
                "ᴄоʍ-инᴄᴨᴇᴋᴛоᴩ": {
                    "emoji": "<:rare_fish:1558444835013140510>",
                    "rarity": "ᴦᴀᴧᴧюцинᴀᴦᴇннᴀя",
                    "chance": 60,
                    "price_from": 37,
                    "price_until": 58
                },
                "ᴧᴀᴛиʍᴇᴩия": {
                    "emoji": "<:epic_fish:1558444833452855327>",
                    "rarity": "иᴄᴛоᴩичᴇᴄᴋᴀя",
                    "chance": 30,
                    "price_from": 46,
                    "price_until": 78
                },
                "ʙᴇᴩиᴧиᴛи": {
                    "emoji": "<:hellfish:1558444862380965958>",
                    "rarity": "ʍᴇᴛᴀʍоᴩɸичᴇᴄᴋᴀя",
                    "chance": 10,
                    "price_from": 67,
                    "price_until": 94
                }
            }
        }

    # METHOD: Получение данных о рыбе
    def get_fish_data(self, rarity):
        fishes = self.fish_info[rarity]

        fish_name = random.choices(
            list(fishes.keys()),
            weights=[fish["chance"] for fish in fishes.values()],
            k=1
        )[0]

        return fish_name

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

    # METHOD: Проверка на отправку сообщения
    async def command_checks(self, interaction: discord.Interaction) -> bool:
        if interaction.channel.id != BotConfig.COMMAND_CHANNEL:
            await self.send_message(interaction,
                (
                    f"{self.dn_em} ϶ᴛᴀ ᴋоʍᴀндᴀ ᴩᴀбоᴛᴀᴇᴛ ᴛоᴧьᴋо ʙ ᴋᴀнᴀᴧᴇ <#{BotConfig.COMMAND_CHANNEL}>!\n"
                    f"\n-# {self.ow_em} ᴨожᴀᴧуйᴄᴛᴀ, ʙʙодиᴛᴇ ᴋоʍᴀнды ʙ оᴄобоʍ ᴋᴀнᴀᴧᴇ."
                )
            , True)
            return False

        if not BotConfig.TRANSACTIONS_AVAILABLE:
            await self.send_message(interaction,
                (
                    f"{self.dn_em} ʙ дᴀнный ʍоʍᴇнᴛ ᴋоʍᴀндᴀ нᴇ доᴄᴛуᴨнᴀ.\n{self.dn_em} циᴩᴋуᴧяция ʙᴀᴧюᴛы ʙᴩᴇʍᴇнно оᴄᴛᴀноʙᴧᴇнᴀ."
                    f"\n\n-# {self.ow_em} ᴨᴩиноᴄиʍ изʙинᴇния зᴀ нᴇудобᴄᴛʙᴀ, ᴨᴩобᴧᴇʍᴀ ᴩᴇɯᴀᴇᴛᴄя."
                )
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

    # METHOD: Для проверки условий перевода валюты
    async def pay_checks(self, interaction, user, points) -> bool:
        if interaction.user.id == user.id:
            msg = (
                f"{self.dn_em} ʙы нᴇ ʍожᴇᴛᴇ ᴨᴇᴩᴇʙᴇᴄᴛи ʙᴀᴧюᴛу ᴄᴀʍоʍу ᴄᴇбᴇ!"
                f"\n\n-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
            )
            await self.send_message(interaction, msg, True)
            return False
        
        if user.bot:
            msg = (
                f"{self.dn_em} ʙы нᴇ ʍожᴇᴛᴇ ᴨᴇᴩᴇʙодиᴛь ʙᴀᴧюᴛу боᴛᴀʍ!"
                f"\n\n-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
            )
            await self.send_message(interaction, msg, True)
            return False
        
        if points <= 25:
            msg = (
                f"{self.dn_em} ᴄуʍʍᴀ ᴨᴇᴩᴇʙодᴀ доᴧжнᴀ быᴛь боᴧьɯᴇ 25 {self.vl_em}!"
                "\n\n-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
            )
            await self.send_message(interaction, msg, True)
            return False

        user_data = await self.manager.get_user_economic(interaction.user.id)
        if user_data["points"] < points:
            msg = (
                f"{self.dn_em} нᴇдоᴄᴛᴀᴛочно ʙᴀᴧюᴛы дᴧя ᴨᴇᴩᴇʙодᴀ!"
                f"\n{self.dn_em} нᴀ ʙᴀɯᴇʍ бᴀᴧᴀнᴄᴇ: {user_data['points']} {self.vl_em}."
                f"\n\n-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
            )
            await self.send_message(interaction, msg, True)
            return False
        
        return True

    # METHOD: Проверка кулдауна
    async def cooldown_check(self, interaction: discord.Interaction, last_time, cooldown) -> bool:
        current_time = time.time()

        time_passed = current_time - last_time

        if time_passed < cooldown:
            seconds_left = int(cooldown - time_passed)
            hours = seconds_left // 3600
            minutes = (seconds_left % 3600) // 60

            await self.send_message(
                interaction,
                (
                    f"{self.wt_em} {interaction.user.mention}, ʙы ужᴇ зᴀбиᴩᴀᴧи нᴀᴦᴩᴀду!\n"
                    f"{self.wt_em} оᴄᴛᴀᴧоᴄь: **{hours} ч. {minutes} мин.**\n\n"
                    f"-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                ),
                True
            )
            return False

        return True

    # METHOD: Метод рыбалки
    async def fishing(self):
        player_chance = random.random()
        is_epic = player_chance >= 0.85

        rarity_type = "epic" if is_epic else "common"

        fish_name = self.get_fish_data(rarity_type)
        fish_data = self.fish_info[rarity_type][fish_name]

        fish_price_from = fish_data["price_from"]
        fish_price_until = fish_data["price_until"]

        reward = random.randint(fish_price_from, fish_price_until)

        return reward, rarity_type, fish_name

    # METHOD: Получить прибыть
    async def get_work(self, interaction: discord.Interaction, cooldown_field, reward, fish_com = False, rarity_type = None, fish_name = None):
        current_time = time.time()
        user_id = interaction.user.id

        await self.manager.add_points(user_id, reward)

        await self.manager.update_user_timer(user_id, cooldown_field, current_time)

        current_points = await self.manager.get_user_points(user_id)

        # LOGIC: Если ф-ция с рыбалкой
        if fish_com:
            fish_data = self.fish_info[rarity_type][fish_name]
            
            fish_emoji = fish_data["emoji"]
            fish_rarity = fish_data["rarity"]
    
            user_id = interaction.user.id
    
            await self.send_message(interaction,
                f"{self.gr_em} {interaction.user.mention}, ʙы ʙыᴧоʙиᴧи ᴩыбу **{fish_name}** {fish_emoji}!\n"
                f"- ``ᴩᴇдᴋоᴄᴛь ᴩыбы``: **{fish_rarity}** {self.st_em}\n"
                f"- ``нᴀᴦᴩᴀдᴀ зᴀ ᴨоиʍᴋу``: **{reward}** {self.vl_em}\n"
                f"{self.gr_em} ʙᴀɯ ᴛᴇᴋущий бᴀᴧᴀнᴄ: {current_points} {self.vl_em}."
                f"\n\n-# {self.cl_em} ᴋуᴧьᴛ ᴦоᴩдиᴛᴄя ʙᴀʍи, нᴇ оᴄᴛᴀʙᴧяйᴛᴇ ᴇᴦо, ᴀ он — ʙᴀᴄ."
            )
            return

        await self.send_message(interaction,
            f"{self.gr_em} {interaction.user.mention}, ʙы ᴨоᴧучиᴧи {reward} {self.vl_em}!\n"
            f"{self.gr_em} ʙᴀɯ ᴛᴇᴋущий бᴀᴧᴀнᴄ: {current_points} {self.vl_em}."
            f"\n\n-# {self.cl_em} ᴋуᴧьᴛ ᴦоᴩдиᴛᴄя ʙᴀʍи, нᴇ оᴄᴛᴀʙᴧяйᴛᴇ ᴇᴦо, ᴀ он — ʙᴀᴄ."
        )

    # COMMAND: Команда "культ" для получения валюты
    @app_commands.command(name="культ", description="Поддержать культ (забрать ежедневный доход).")
    @app_commands.guild_only()
    async def claim(self, interaction: discord.Interaction):
        # LOGIC: Проверки условий перед использованием
        if not await self.command_checks(interaction):
            return

        user_data = await self.manager.get_user_economic(interaction.user.id)
        user_cooldown = user_data["last_claim"]
        cooldown = 14400
        if not await self.cooldown_check(interaction, user_cooldown, cooldown):
            return

        reward = int(random.randint(13, 28))

        await self.get_work(interaction, "last_claim", reward)

    # COMMAND: Команда "рыбалка" для получения валюты
    @app_commands.command(name="рыбалка", description="Порыбачить ради прибыли.")
    @app_commands.guild_only()
    async def fish(self, interaction: discord.Interaction):
        # LOGIC: Проверки условий перед использованием
        if not await self.command_checks(interaction):
            return

        user_data = await self.manager.get_user_economic(interaction.user.id)
        user_cooldown = user_data["last_fish"]
        cooldown = 18000
        if not await self.cooldown_check(interaction, user_cooldown, cooldown):
            return

        reward, rarity_type, fish_name = await self.fishing()

        await self.get_work(interaction, "last_fish", reward, True, rarity_type, fish_name)

    # COMMAND: Команда "бонус" для получения валюты
    @app_commands.command(name="бонус", description="Забрать дополнительную награду.")
    @app_commands.guild_only()
    async def bonus(self, interaction: discord.Interaction):
        # LOGIC: Проверки условий перед использованием
        if not await self.command_checks(interaction):
            return

        user_data = await self.manager.get_user_economic(interaction.user.id)
        user_cooldown = user_data["last_bonus"]
        cooldown = 28800
        if not await self.cooldown_check(interaction, user_cooldown, cooldown):
            return

        reward = int(random.randint(20, 39))

        await self.get_work(interaction, "last_bonus", reward)

    # COMMAND: Команда "заплатить" для передачи пользователю валюты
    @app_commands.command(name="заплатить", description="Передать пользователю валюту.")
    @app_commands.describe(user="Пользователь.", points="Кол-во валюты.")
    @app_commands.guild_only()
    async def pay(self, interaction: discord.Interaction, user: discord.User, points: int):
        # LOGIC: Проверки условий перед использованием
        if not await self.command_checks(interaction):
            return
        if not await self.pay_checks(interaction, user, points):
            return
        
        # METHOD: Подверждение действия и дальнейшее его продвижение
        async def confirm_action(confirm_interaction: discord.Interaction):
            
            # LOGIC: Выдача валюты пользователю и устранение валюты от переданного игрока
            try:
                user_points = int(-points)
                await self.manager.add_points(confirm_interaction.user.id, user_points)
    
                target_points = int(points)
                await self.manager.add_points(user.id, target_points)
            
            # LOGIC: Неудачный перевод
            except Exception as e:
                await self.send_message(confirm_interaction, 
                    (
                        f"{self.dn_em} ᴨᴩоизоɯᴧᴀ оɯибᴋᴀ ᴨᴩи ᴨᴇᴩᴇʙодᴇ:\n"
                        f"```{str(e)}```\n\n"
                        f"-# {self.ow_em} ᴨᴩобᴧᴇʍᴀ ᴄ ᴨᴇᴩᴇʙодоʍ, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                    )
                , True)
                return

            # LOGIC: Получаем новую информацию для отображения и канал логов
            target_data = await self.manager.get_user_economic(user.id)
            channel = self.bot.get_channel(BotConfig.LOG_CHANNEL)
            
            # LOGIC: Отправка сообщения пользователю
            msg = (
                f"{self.gr_em} ᴨоᴧьзоʙᴀᴛᴇᴧь, {confirm_interaction.user.mention}, ᴨᴇᴩᴇʙᴇᴧ ʙᴀᴧюᴛу {user.mention}.\n"
                f"{self.gr_em} ᴩᴀзʍᴇᴩ ᴨᴇᴩᴇʙᴇдённой ᴄуʍʍы: `{points}` {self.vl_em}\n"
                f"{self.gr_em} новый баланс {user.mention}: `{target_data['points']}` {self.vl_em}"
                f"\n\n-# {self.cl_em} ᴋуᴧьᴛ ᴦоᴩдиᴛᴄя ʙᴀʍи, нᴇ оᴄᴛᴀʙᴧяйᴛᴇ ᴇᴦо, ᴀ он — ʙᴀᴄ."
            )
            await self.send_message(confirm_interaction, msg, False)

            # LOGIC: Фиксируем в логах
            l_msg = (
                f"### {self.cl_em} ᴨᴇᴩᴇʙод ʙᴀᴧюᴛы.\n"
                f"{self.at_em} ᴨоᴧьзоʙᴀᴛᴇᴧь {interaction.user.mention} ᴨᴇᴩᴇʙёᴧ иᴦᴩоᴋу {user.mention} ʙᴀᴧюᴛу\n"
                f"{self.at_em} ᴩᴀзʍᴇᴩ ᴨᴇᴩᴇʙᴇдᴇнной ʙᴀᴧюᴛы: {points} {self.vl_em}\n\n"
                f"{self.at_em} новый баланс {user.mention}: {target_data['points']} {self.vl_em}"
                f"\n\n-# {self.ow_em} ʙ ᴄᴧучᴀᴇ нᴇзᴀᴋонноᴄᴛи — ʙы ʙ ᴨᴩᴀʙᴇ нᴀᴋᴀзᴀᴛь ᴇᴦо."
            )
            await self.send_message(channel, l_msg)

        # LOGIC: Отправка сообщения с подверждением/отменой
        view = ConfirmComponent(
            on_confirm=confirm_action
        )

        await interaction.response.send_message(
            view=view,
            ephemeral=True
        )

        view.message = await interaction.original_response()

    # @app_commands.command(name="ограбить", description="Ограбить другого игрока.")
    # @app_commands.describe(user="Кого хотите ограбить?")
    # @app_commands.guild_only()
    # async def rob(self, interaction: discord.Interaction, user: discord.User):
    #     if interaction.channel.id != COMMANDS_CHANNEL and interaction.channel.id != MOD_COMMANDS_CHANNEL:
    #         await safe_send(interaction, f"<:accessdeniedemoji:1517986918573408318> Эта команда работает только в канале <#{COMMANDS_CHANNEL}>!", ephemeral=True)
    #         return
    #     if interaction.user.id == user.id:
    #         await safe_send(interaction, "<:accessdeniedemoji:1517986918573408318> Вы не можете ограбить самого себя!", ephemeral=True)
    #         return
    #     if user.bot:
    #         await safe_send(interaction, "<:accessdeniedemoji:1517986918573408318> Вы не можете ограбить ботов!", ephemeral=True)
    #         return
    #     robber_data = await manager.get_user_economic(interaction.user.id)
    #     victim_data = await manager.get_user_economic(user.id)
    #     if robber_data["points"] < 30:
    #         await safe_send(interaction, f"<:accessdeniedemoji:1517986918573408318> У вас слишком мало денег! Нужно хотя бы 30 монет, чтобы начать грабить.", ephemeral=True)
    #         return
    #     if victim_data["points"] < 30:
    #         await safe_send(interaction, f"<:accessdeniedemoji:1517986918573408318> У <@{user.id}> слишком мало денег!\nУ него всего {victim_data['points']} монет.", ephemeral=True)
    #         return
    #     current_time = time.time()
        
    #     time_passed = current_time - robber_data["last_rob"]
    #     if time_passed < 43200:
    #         seconds_left = int(43200 - time_passed)
    #         hours = seconds_left // 3600
    #         minutes = (seconds_left % 3600) // 60
    #         seconds = seconds_left % 60
    #         time_left = f"{hours} ч. {minutes} мин." if hours > 0 else (f"{minutes} мин. {seconds} сек." if minutes > 0 else f"{seconds} сек.")
    #         await safe_send(interaction, f"<:accessdeniedemoji:1517986918573408318> Вы не можете грабить так часто! Будет доступно: **{time_left}**.", ephemeral=True)
    #         return
    #     success = random.random() < 0.4
    #     if success:
    #         new_points = random.randint(8, 21)
    #         await manager.update_user_economic(interaction.user.id, int(robber_data["points"]+new_points), robber_data["trees"], robber_data["bugs"], robber_data["animals"], robber_data["werewolfs"], robber_data["last_claim"], robber_data["last_water"], robber_data["last_collect"], robber_data["last_fish"], robber_data["last_bonus"], current_time)
    #         await manager.update_user_economic(user.id, int(victim_data["points"]-new_points), victim_data["trees"], victim_data["bugs"], victim_data["animals"], victim_data["werewolfs"], victim_data["last_claim"], victim_data["last_water"], victim_data["last_collect"], victim_data["last_fish"], victim_data["last_bonus"], victim_data["last_rob"])
            
    #         embed = discord.Embed(
    #             title="<:moneybagemoji:1518230296078843964> **ⲩⲥⲡⲉɯⲏⲟⲉ ⲟⲅⲣⲁⳝⲗⲉⲏυⲉ!**",
    #             description=f"ʙы оᴦᴩᴀбиᴧи <@{user.id}> и уᴋᴩᴀᴧи `{new_points}` <:physpoints:1515371982571704361>!",
    #             color=discord.Color.green()
    #         )
    #         embed.add_field(
    #             name="ʙᴀɯ бᴀᴧᴀнᴄ",
    #             value=f"**{int(robber_data['points']+new_points)}** <:physpoints:1515371982571704361>",
    #             inline=True
    #         )
    #         embed.add_field(
    #             name="бᴀᴧᴀнᴄ жᴇᴩᴛʙы",
    #             value=f"**{int(victim_data['points']-new_points)}** <:physpoints:1515371982571704361>",
    #             inline=True
    #         )
    #         embed.set_footer(text="ну и зᴧодᴇй жᴇ ʙы...")
    #         try:
    #             await user.send(f"<:moneybagemoji:1518230296078843964> ʙᴀᴄ оᴦᴩᴀбиᴧ <@{interaction.user.id}> нᴀ `{new_points}` <:physpoints:1515371982571704361>!")
    #         except:
    #             pass
            
    #         await safe_send(interaction, embed=embed)
            
    #     else:
    #         new_points = random.randint(4, 13)
    #         await manager.update_user_economic(interaction.user.id, int(robber_data["points"]-new_points), robber_data["trees"], robber_data["bugs"], robber_data["animals"], robber_data["werewolfs"], robber_data["last_claim"], robber_data["last_water"], robber_data["last_collect"], robber_data["last_fish"], robber_data["last_bonus"], current_time)
    #         await manager.update_user_economic(user.id, int(victim_data["points"]+new_points), victim_data["trees"], victim_data["bugs"], victim_data["animals"], victim_data["werewolfs"], victim_data["last_claim"], victim_data["last_water"], victim_data["last_collect"], victim_data["last_fish"], victim_data["last_bonus"], victim_data["last_rob"])
            
    #         embed = discord.Embed(
    #             title="<:accessdeniedemoji:1517986918573408318> **ⲏⲉⲩⲇⲁɥⲏⲁя ⲡⲟⲡыⲧⲕⲁ!**",
    #             description=f"ʙы ᴨоᴨыᴛᴀᴧиᴄь оᴦᴩᴀбиᴛь <@{user.id}>,\nно у ʙᴀᴄ ничᴇᴦо нᴇ ʙыɯᴧо! <:moneybagemoji:1518230296078843964>",
    #             color=discord.Color.orange()
    #         )
    #         embed.add_field(
    #             name="ɯᴛᴩᴀɸ",
    #             value=f"**{new_points}** <:physpoints:1515371982571704361>",
    #             inline=True
    #         )
    #         embed.add_field(
    #             name="ʙᴀɯ бᴀᴧᴀнᴄ",
    #             value=f"**{int(robber_data['points']-new_points)}** <:physpoints:1515371982571704361>",
    #             inline=True
    #         )
    #         embed.set_footer(text="ʙоᴩ228...")
    #         try:
    #             await user.send(f"<:moneybagemoji:1518230296078843964> <@{interaction.user.id}> ᴨыᴛᴀᴧᴄя ʙᴀᴄ оᴦᴩᴀбиᴛь нᴀ `{new_points}` <:physpoints:1515371982571704361>, но у нᴇᴦо ничᴇᴦо нᴇ ʙыɯᴧо!")
    #         except:
    #             pass
            
    #         await safe_send(interaction, embed=embed)

# LOGIC: Запуск кога
async def setup(bot):
    await bot.add_cog(EconomicCog(bot))