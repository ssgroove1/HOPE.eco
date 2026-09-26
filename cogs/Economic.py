import discord, asyncio, time, random
from discord import app_commands
from pathlib import Path
from datetime import datetime
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

    # METHOD: Отправка сообщения с View
    async def send_message(self, destination: discord.Interaction, content: str, is_ephemeral=False):
        try:
            view = DefaultComponent(content)

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

        except Exception as e:
            print(
                f"❌ Не удалось отправить сообщение пользователю: "
                f"{type(e).__name__}: {e}"
            )

    # METHOD: Получение валюты
    async def get_work(self, interaction: discord.Interaction, user_id, reward, cooldown, cooldown_field):
        user_data = await self.manager.get_user_economic(user_id)
        current_time = time.time()

        # Получаем время последнего использования нужной команды
        last_time = user_data[cooldown_field]
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
            return
        
        new_points = user_data["points"] + reward
        user_data[cooldown_field] = current_time

        await self.manager.update_user_economic(
            user_id,
            new_points,
            user_data["last_claim"],
            user_data["last_water"],
            user_data["last_collect"],
            user_data["last_fish"],
            user_data["last_bonus"],
            user_data["last_rob"]
        )
        
        await self.send_message(interaction,
            f"{self.gr_em} {interaction.user.mention}, ʙы ᴨоᴧучиᴧи {reward} {self.vl_em}!\n"
            f"{self.gr_em} ʙᴀɯ ᴛᴇᴋущий бᴀᴧᴀнᴄ: {new_points} {self.vl_em}."
            f"\n\n-# {self.cl_em} ᴋуᴧьᴛ ᴦоᴩдиᴛᴄя ʙᴀʍи, нᴇ оᴄᴛᴀʙᴧяйᴛᴇ ᴇᴦо, ᴀ он — ʙᴀᴄ."
            )

    @app_commands.command(name="культ", description="Поддержать культ (забрать ежедневный доход).")
    @app_commands.guild_only()
    async def claim(self, interaction: discord.Interaction):
        if interaction.channel.id != BotConfig.COMMAND_CHANNEL:
            await self.send_message(interaction,
                (
                    f"{self.dn_em} ϶ᴛᴀ ᴋоʍᴀндᴀ ᴩᴀбоᴛᴀᴇᴛ ᴛоᴧьᴋо ʙ ᴋᴀнᴀᴧᴇ <#{BotConfig.COMMAND_CHANNEL}>!\n"
                    f"\n-# {self.ow_em} ᴨожᴀᴧуйᴄᴛᴀ, ʙʙодиᴛᴇ ᴋоʍᴀнды ʙ оᴄобоʍ ᴋᴀнᴀᴧᴇ."
                )
            , True)
            return

        user_id = interaction.user.id
        reward = random.randint(7, 19)
        cooldown = 14400

        await self.get_work(interaction, user_id, reward, cooldown, "last_claim")

    # @app_commands.command(name="рыбалка", description="Порыбачить для прибыли.")
    # @app_commands.guild_only()
    # async def fish(self, interaction: discord.Interaction):
    #     if interaction.channel.id != BotConfig.COMMAND_CHANNEL:
    #         await safe_send(interaction, f"<:accessdeniedemoji:1517986918573408318> Эта команда работает только в канале <#{BotConfig.COMMAND_CHANNEL}>!", ephemeral=True)
    #         return
    #     await interaction.response.defer()
    #     user_id = interaction.user.id
    #     user_data = await self.manager.get_user_economic(user_id)
    #     current_time = time.time()
    #     time_passed = current_time - user_data["last_fish"]

    #     if time_passed < 28800:
    #         seconds_left = int(28800 - time_passed)
    #         hours = seconds_left // 3600
    #         minutes = (seconds_left % 3600) // 60
    #         await safe_send(interaction, f"**<:accessdeniedemoji:1517986918573408318> {interaction.user.mention}, вы уже забирали награду!**\n⌛ Осталось: **{hours} ч. {minutes} мин.**", ephemeral=True)
    #         return
    #     chance = random.random()
    #     fish_text = ""
    #     if chance < 0.01:
    #         fish_text = "ⲏⲁⲥⲧⲟяպⲉⲅⲟ ⲙⲉⲅⲁⲗⲁⲇⲟⲏⲁ! <:megaladonemoji:1518011720499593246>"
    #         reward = random.randint(124, 157)
    #         role = interaction.guild.get_role(1518011868709388339)
    #         if role:
    #             await interaction.user.add_roles(role, reason=f"Выловил улов!")
    #             await safe_send(interaction, "<:trophyemoji:1517928090708345032> Вам выдана роль за улов!", ephemeral=True)
    #     elif chance < 0.1:
    #         fish_text = "ⲿυⲃⲩю ⲁⲕⲩⲗⲩ! <:sharkemoji:1518009750078492944>"
    #         reward = random.randint(27, 36)
    #         role = interaction.guild.get_role(1518010342410686606)
    #         if role:
    #             await interaction.user.add_roles(role, reason=f"Выловил улов!")
    #             await safe_send(interaction,"<:trophyemoji:1517928090708345032> Вам выдана роль за улов!", ephemeral=True)
    #     elif chance < 0.3:
    #         fish_text = "պⲩⲕⲩ! <:fish2emoji:1518009317129715843>"
    #         reward = random.randint(11, 19)
    #     else:  
    #         fish_text = "ⲟⲕⲩⲏя. <:fish1emoji:1518008900941774870>"
    #         reward = random.randint(4, 8)

    #     new_points = user_data["points"] + reward

    #     await self.manager.update_user_economic(user_id, new_points, user_data["trees"], user_data["bugs"], user_data["animals"], user_data["werewolfs"], current_time, user_data["last_water"], user_data["last_collect"], current_time, user_data["last_bonus"], user_data["last_rob"])
    #     await safe_send(interaction, f"{interaction.user.mention}, ʙы ʙыᴧоʙиᴧи **{fish_text}** ʙᴀɯᴀ нᴀᴦᴩᴀдᴀ: **{reward} <:physpoints:1515371982571704361>**!\nʙᴀɯ ᴛᴇᴋущий бᴀᴧᴀнᴄ: **{new_points} <:physpoints:1515371982571704361>**.")

    @app_commands.command(name="бонус", description="Забрать дополнительную награду.")
    @app_commands.guild_only()
    async def bonus(self, interaction: discord.Interaction):
        if interaction.channel.id != BotConfig.COMMAND_CHANNEL:
            await self.send_message(interaction,
                (
                    f"{self.dn_em} ϶ᴛᴀ ᴋоʍᴀндᴀ ᴩᴀбоᴛᴀᴇᴛ ᴛоᴧьᴋо ʙ ᴋᴀнᴀᴧᴇ <#{BotConfig.COMMAND_CHANNEL}>!\n"
                    f"\n-# {self.ow_em} ᴨожᴀᴧуйᴄᴛᴀ, ʙʙодиᴛᴇ ᴋоʍᴀнды ʙ оᴄобоʍ ᴋᴀнᴀᴧᴇ."
                )
            , True)
            return

        user_id = interaction.user.id
        reward = random.randint(3, 11)
        cooldown = 28800

        await self.get_work(interaction, user_id, reward, cooldown, "last_bonus")

    # @app_commands.command(name="казино", description="Дэпнуть...")
    # @app_commands.describe(bet="Сумма ставки.")
    # @app_commands.guild_only()
    # async def casino(self, interaction: discord.Interaction, bet: int):
    #     if interaction.channel.id != COMMANDS_CHANNEL and interaction.channel.id != MOD_COMMANDS_CHANNEL:
    #         await safe_send(interaction, f"<:accessdeniedemoji:1517986918573408318> Эта команда работает только в канале <#{COMMANDS_CHANNEL}>!", ephemeral=True)
    #         return
    #     if bet < 10:
    #         await safe_send(interaction, f"<:accessdeniedemoji:1517986918573408318> Минимальная ставка: `10` <:physpoints:1515371982571704361>!", ephemeral=True)
    #         return
    #     if bet > 100:
    #         await safe_send(interaction, f"<:accessdeniedemoji:1517986918573408318> Максимальная ставка: `100` <:physpoints:1515371982571704361>!", ephemeral=True)
    #         return
    #     user_data = await manager.get_user_economic(interaction.user.id)
    #     if user_data["points"] < bet:
    #         await safe_send(interaction, f"<:accessdeniedemoji:1517986918573408318> Недостаточно монет! У вас: `{user_data['points']}` <:physpoints:1515371982571704361>", ephemeral=True)
    #         return
    #     symbols = ["<a:cherryemoji:1518682902827896973>", "<a:lemonemoji:1518683734411444224>", "<a:orangeemoji:1518685108578680863>", "<a:grapesemoji:1518685654907621546>", "<a:littlediamondemoji:1518554727023902730>", "<a:staremoji:1518554397750202460>", "<a:hakariemoji:1518552999214055424>"]
        
    #     slot1 = random.choice(symbols)
    #     slot2 = random.choice(symbols)
    #     slot3 = random.choice(symbols)

    #     win = False
    #     multiplier = 0
    #     text = ""
    #     winning_combos = {
    #         "<a:hakariemoji:1518552999214055424>": (5, "**джᴇᴋᴨоᴛ! ᴨоᴧучᴀᴇᴛ ᴄиᴧу хᴀᴋᴀᴩи!**"),
    #         "<a:littlediamondemoji:1518554727023902730>": (3.5, "**ᴀᴧʍᴀзнᴀя ᴧихоᴩᴀдᴋᴀ!**"),
    #         "<a:staremoji:1518554397750202460>": (2.75, "**ᴄᴇᴦодняɯний зʙᴇздоᴨᴀд!**"),
    #         "<a:cherryemoji:1518682902827896973>": (2.25, "**иᴄᴨоᴧьзуᴇᴛ оᴦнᴇʙую ʍощь ʙиɯни из ᴘᴠᴢ!**"),
    #         "<a:lemonemoji:1518683734411444224>": (2, "**ᴧиʍонᴀдноᴇ нᴀᴄᴧᴀждᴇньᴇ!**"),
    #         "<a:orangeemoji:1518685108578680863>": (2, "**ᴀᴨᴇᴧьᴄинᴋи!**"),
    #         "<a:grapesemoji:1518685654907621546>": (2.25, "**ᴧучɯᴇᴇ ʙино!**")
    #     }

    #     if slot1 == slot2 == slot3 and slot1 in winning_combos:
    #         multiplier, text = winning_combos[slot1]
    #         win = True
    #     elif slot1 == slot2 or slot2 == slot3 or slot1 == slot3:
    #         multiplier = 1.15
    #         win = True
    #         text = "**<:accessemoji:1518684370410541158> дʙᴇ одинᴀᴋоʙых!**"
    #     else:
    #         text = "<:accessdeniedemoji:1517986918573408318> **ничᴇᴦо нᴇ ʙыᴨᴀᴧо...**"
    #     if win:
    #         winnings = int(bet * multiplier)
    #         await manager.update_user_economic(interaction.user.id, int(user_data["points"]+winnings), user_data["trees"], user_data["bugs"], user_data["animals"], user_data["werewolfs"], user_data["last_claim"], user_data["last_water"], user_data["last_collect"], user_data["last_fish"], user_data["last_bonus"], user_data["last_rob"])
    #         embed = discord.Embed(
    #             title="🎰 ᴍᴀᴄʜɪɴᴇ's sʟᴏᴛs",
    #             description=f"{slot1} {slot2} {slot3}\n\n"
    #                         f"{text}\n"
    #                         f"<:moneybagemoji:1518230296078843964> ʙыиᴦᴩыɯ: `{winnings}` <:physpoints:1515371982571704361> (x{multiplier})",
    #             color=discord.Color.green()
    #         )
    #     else:
    #         await manager.update_user_economic(interaction.user.id, int(user_data["points"]-bet), user_data["trees"], user_data["bugs"], user_data["animals"], user_data["werewolfs"], user_data["last_claim"], user_data["last_water"], user_data["last_collect"], user_data["last_fish"], user_data["last_bonus"], user_data["last_rob"])
    #         embed = discord.Embed(
    #             title="🎰 ᴍᴀᴄʜɪɴᴇ's sʟᴏᴛs",
    #             description=f"{slot1} {slot2} {slot3}\n\n"
    #                         f"{text}\n"
    #                         f"<:accessdeniedemoji:1517986918573408318> ᴨоᴛᴇᴩяно: `{bet}` <:physpoints:1515371982571704361>",
    #             color=discord.Color.red()
    #         )
    #     new_balance = user_data["points"] + (winnings if win else -bet)
    #     embed.add_field(
    #         name="<:moneybagemoji:1518230296078843964> ʙᴀɯ бᴀᴧᴀнᴄ",
    #         value=f"`{new_balance}` <:physpoints:1515371982571704361>",
    #         inline=False
    #     )
    #     embed.set_footer(text="удᴀчᴀ доᴄᴛиᴦнᴇᴛ ʙᴀᴄ! 🍀")
        
    #     await safe_send(interaction, embed=embed)

    # @app_commands.command(name="заплатить", description="Передать пользователю монет.")
    # @app_commands.describe(user="Пользователь.", points="Кол-во монет.")
    # @app_commands.guild_only()
    # async def pay(self, interaction: discord.Interaction, user: discord.User, points: int):
    #     if interaction.channel.id != COMMANDS_CHANNEL and interaction.channel.id != MOD_COMMANDS_CHANNEL:
    #         await safe_send(interaction, f"<:accessdeniedemoji:1517986918573408318> Эта команда работает только в канале <#{COMMANDS_CHANNEL}>!", ephemeral=True)
    #         return
    #     if interaction.user.id == user.id:
    #         await safe_send(interaction, "<:accessdeniedemoji:1517986918573408318> Вы не можете перевести монеты самому себе!", ephemeral=True)
    #         return
    #     if user.bot:
    #         await safe_send(interaction, "<:accessdeniedemoji:1517986918573408318> Вы не можете переводить монеты ботам!", ephemeral=True)
    #         return
    #     if points <= 0:
    #         await safe_send(interaction, "<:accessdeniedemoji:1517986918573408318> Сумма должна быть больше 0!", ephemeral=True)
    #         return
    #     MIN_PAY = 5
    #     if points < MIN_PAY:
    #         await safe_send(interaction, f"<:accessdeniedemoji:1517986918573408318> Минимальная сумма для перевода - {MIN_PAY} монет!", ephemeral=True)
    #         return
    #     MAX_PAY = 10000
    #     if points > MAX_PAY:
    #         await safe_send(interaction, f"<:accessdeniedemoji:1517986918573408318> Максимальная сумма для перевода - {MAX_PAY} монет!", ephemeral=True)
    #         return
    #     user_data = await manager.get_user_economic(interaction.user.id)
    #     target_data = await manager.get_user_economic(user.id)
    #     if user_data["points"] < points:
    #         await safe_send(interaction, f"<:accessdeniedemoji:1517986918573408318> Недостаточно монет! У вас: {user_data['points']} монет.", ephemeral=True)
    #         return
    #     try:
    #         await manager.update_user_economic(interaction.user.id, int(user_data["points"]-points), user_data["trees"], user_data["bugs"], user_data["animals"], user_data["werewolfs"], user_data["last_claim"], user_data["last_water"], user_data["last_collect"], user_data["last_fish"], user_data["last_bonus"], user_data["last_rob"])
    #         await manager.update_user_economic(user.id, int(target_data["points"]+points), target_data["trees"], target_data["bugs"], target_data["animals"], target_data["werewolfs"], target_data["last_claim"], target_data["last_water"], target_data["last_collect"], target_data["last_fish"], target_data["last_bonus"], target_data["last_rob"])
    #     except Exception as e:
    #         await safe_send(interaction, f"❌ Произошла ошибка при переводе: {str(e)}", ephemeral=True)
    #         return
    #     embed = discord.Embed(
    #         title="<:moneybagemoji:1518230296078843964> уᴄᴨᴇɯный ᴨᴇᴩᴇʙод!",
    #         color=discord.Color.darker_grey()
    #     )
    #     embed.add_field(
    #         name="оᴛᴨᴩᴀʙиᴛᴇᴧь",
    #         value=f"<@{interaction.user.id}>",
    #         inline=True
    #     )
    #     embed.add_field(
    #         name="ᴨоᴧучᴀᴛᴇᴧь",
    #         value=f"<@{user.id}>",
    #         inline=True
    #     )
    #     embed.add_field(
    #         name="ᴨоᴧучиᴧ",
    #         value=f"**{points}** <:physpoints:1515371982571704361>",
    #         inline=True
    #     )
    #     await safe_send(interaction, embed=embed)

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