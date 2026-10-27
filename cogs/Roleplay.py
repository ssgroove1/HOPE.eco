import discord, random
from discord import app_commands
from pathlib import Path
from discord.ext import commands

# Импорт ваших собственных настроек и функций из корня проекта
from config import BotConfig
from database.db_logic import DB_Manager

BASE_DIR = Path(__file__).resolve().parent.parent
gifs_dir = BASE_DIR / "gifs"

print(f"🔍 Бот ищет папку с гифками по пути: {gifs_dir}")

# LOGIC: Выгрузка гифок из .txt
gifs_data = {}
gif_files = ["hug", "kiss", "hello", "flower", "pat", "kill", "bite", "cry", "dance", "ice_cream", "smile", "pokemon"]

for name in gif_files:
    file_path = gifs_dir / f"{name}_gifs.txt"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            # Читаем строки, очищаем от пробелов и убираем пустые строки
            lines = [line.strip() for line in f.readlines() if line.strip()]
            gifs_data[f"{name}_gifs"] = lines
            # Выводим в консоль успешный статус, чтобы вы видели, что файлы прочитались
            print(f"✅ Успешно загружен файл: {name}_gifs.txt (Найдено гифок: {len(lines)})")
    except FileNotFoundError:
        print(f"⚠️ Файл НЕ НАЙДЕН по пути: {file_path}. Инициализирован пустой список.")
        gifs_data[f"{name}_gifs"] = []

# LOGIC: Выгрузка скаченных гифок
secret_gifs = []
secret_direction = BASE_DIR / "gifs" / "secret"

for file_path in secret_direction.glob("*.gif"):
    secret_gifs.append(file_path)

# COMPANENT: Компанент интерактивного действия
class InteractiveComponent(discord.ui.LayoutView):
    def __init__(self, cog, color, title, action, username1, username2, gif):
        super().__init__(timeout=None)
        self.cog = cog

        self.InfoContainer = discord.ui.Container(
            discord.ui.TextDisplay(
                f"## {title}\n"
                f"{username1} {action} {username2} {self.cog.lv_em}",
            ),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media=gif,
                    description="interactive_gif",
                ),
            ),
            discord.ui.Separator(
                visible=True,
                spacing=discord.SeparatorSpacing.small,
            ),
            discord.ui.TextDisplay(
                content=f"-# {self.cog.ow_em} ʙᴄᴇᴦо нᴀиᴧучɯᴇᴦо ʙ жизнᴇ, ᴋуᴧьᴛ ᴦоᴩд зᴀ ʙᴀᴄ!"
            ),
            accent_colour=color,
        )

        self.add_item(self.InfoContainer)

# COMPANENT: Компанент простого текстового сообщения
class DefaultComponent(discord.ui.LayoutView):
    def __init__(
        self,
        content,
    ):
        super().__init__()

        # LOGIC: Создание контейнера для текстового сообщения
        self.InfoContainer = discord.ui.Container(
            discord.ui.TextDisplay(content=content),
        )
        self.add_item(self.InfoContainer)

# LOGIC: Основной функционал интерактивных ф-ций
class RoleplayCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.manager = DB_Manager(BotConfig.DB_PATH)

        # VARIABLE: Списки с синонимами
        self.hello_variable = [
            "ᴨᴩиʙᴇᴛᴄᴛʙуᴇᴛ", "ʙᴄᴛᴩᴇчᴀᴇᴛ", "здоᴩоʙᴀᴇᴛᴄя", "бᴧᴀᴦоᴨᴩиʙᴇᴛᴄᴛʙуᴇᴛ"
        ]
        self.hug_variable = [
            "обниʍᴀᴇᴛ", "ᴨᴩижиʍᴀᴇᴛ", "зᴀᴋᴧючиᴧ ʙ объяᴛия", "ᴨᴩижᴀᴧ ᴋ ᴄᴇᴩдцу"
        ]
        self.kiss_variable = [
            "цᴇᴧуᴇᴛ", "чʍоᴋᴀᴇᴛ", "ᴩᴀᴄцᴇᴧоʙᴀᴇᴛ", "оᴛᴨᴩᴀʙᴧяᴇᴛ ᴨоцᴇᴧуй"
        ]
        self.pat_variable = [
            "ᴦᴧᴀдиᴛ", "ᴨоᴦᴧᴀжиʙᴀᴇᴛ", "ᴧᴀᴄᴋᴀᴇᴛ", "ᴩᴀзᴦᴧᴀжиʙᴀᴇᴛ"
        ]
        self.bite_variable = [
            "ᴋуᴄᴀᴇᴛ", "уᴋуᴄыʙᴀᴇᴛ", "ᴨᴩобуᴇᴛ нᴀ ʙᴋуᴄ", "цᴀᴨᴀᴇᴛ", "ʙᴨиʙᴀᴇᴛᴄя зубᴀʍи ʙ"
        ]
        self.kill_variable = [
            "убиʙᴀᴇᴛ", "ᴧиᴋʙидиᴩуᴇᴛ", "ᴨоᴩᴀжᴀᴇᴛ", "ᴧиɯᴀᴇᴛ жизни", "ᴦубиᴛ", "ᴩᴀниᴛ"
        ]
        self.secret_variable = [
            "ᴛᴩᴀхнуᴧ", "оᴛыиʍᴇᴧ", "зᴀняᴧᴄя ᴄᴇᴋᴄоʍ ᴄ", "оᴛжᴀᴩиᴧ", "зᴀᴛᴀщиᴧ ʙ ᴨоᴄᴛᴇᴧь", "ᴄоʙоᴋуᴨᴧяᴇᴛ ᴄ", "ʙздᴩочнуᴧ нᴀ"
        ]
        self.verbs = [
            "ᴧᴀᴄᴋоʙо", "нᴇжно", "ᴧюбоʙно", "ʍяᴦᴋо", "ᴛᴇᴨᴧо", "ʍиᴧо", "зᴀбоᴛᴧиʙо", "дᴩужᴇᴄᴋи"
        ]

        # VARIABLE: Эмодзи для сообщений
        self.lv_em = "<a:love_emoji:1563969755847721170>"
        self.hello_em = "<a:hello_emoji:1564009821894869165>"
        self.kiss_em = "<a:kiss_emoji:1563970683501944872>"
        self.hug_em = "<a:hug_emoji:1563970685121077278>"
        self.pat_em = "<a:pat_emoji:1564002930691014860>"
        self.bite_em = "<a:bite_emoji:1564002932960010423>"
        self.kill_em = "<a:kill_emoji:1564002935996944505>"
        self.secret_em = "<a:secret_emoji:1564002934528671785>"
        self.ow_em = "<a:owner_emoji:1552781248236097546>"
        self.gr_em = "<a:alright_emoji:1552752070262521917>"
        self.mm_em = "<a:member_emoji:1553129529378078842>"
        self.dn_em = "<a:denied_emoji:1552780290609512658>"
        self.gm_em = "<a:star_emoji:1553416240142360627>"

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

    # METHOD: Выполнение ролевых действий
    async def _execute_action(
        self, 
        interaction: discord.Interaction, 
        member: discord.Member, 
        gifs_key: str,
        color,
        title: str, 
        action_verb: str,
        self_error: str,
        downloaded: bool = False,
        file = None,
    ):
        # LOGIC: Проверки
        if member.id == interaction.user.id:
            msg = self_error + f"\n\n-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
            await self.send_message(interaction, msg, True)
            return

        if member.bot:
            msg = f"{self.dn_em} ᴨᴩоᴄᴛиᴛᴇ, {interaction.user.mention}, но ʙы нᴇ ʍожᴇᴛᴇ...\n{self.dn_em} иᴄᴨоᴧьзоʙᴀᴛь дᴇйᴄᴛʙия нᴀ боᴛᴀх!\n\n-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
            await self.send_message(
                interaction, 
                msg, 
                True
            )
            return

        # LOGIC: Проверка, что гифки в виде ссылок
        if not downloaded:
            # LOGIC: Получаем определенные гифки
            if not gifs_key.endswith("_gifs"):
                pure_name = gifs_key
                gifs_key = f"{pure_name}_gifs"
            else:
                pure_name = gifs_key.replace("_gifs", "")

            # LOGIC: Список с гифками этими
            gifs_list = gifs_data.get(gifs_key, [])

            if not gifs_list:
                msg = f"{self.dn_em} нᴇᴛ доᴄᴛуᴨных ᴦиɸоᴋ ʙ ɸᴀйᴧᴀх боᴛᴀ!\n{self.dn_em} ᴨᴩоʙᴇᴩьᴛᴇ ɸᴀйᴧ ʙ боᴛᴇ: {pure_name}_gifs.txt!\n\n-# {self.ow_em} ᴨᴩобᴧᴇʍᴀ ᴄ ɸᴀйᴧᴀʍи, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                await self.send_message(
                    interaction, 
                    msg, 
                    True
                )
                return

        # LOGIC: Выбираем гифку
        if not downloaded:
            random_gif = random.choice(gifs_list)
        else:
            random_gif = gifs_key

        await interaction.response.defer(ephemeral=False)

        # LOGIC: Отправляем сообщение
        view = InteractiveComponent(self, color, title, action_verb, interaction.user.mention, member.mention, random_gif)
        if not downloaded:
            await interaction.followup.send(
                view=view,
                ephemeral=False
            )
        # LOGIC: Отправка сообщения со скаченными в программе гифками
        else:
            await interaction.followup.send(
                view=view,
                ephemeral=False,
                file=file
            )

    # COMMAND: Команда интерактивного действия "приветствие"
    @app_commands.command(name="приветствие", description="Приветствие пользователя.")
    @app_commands.describe(member="Пользователя, которому хотите передать привет.")
    @app_commands.guild_only()
    async def hello_command(self, interaction: discord.Interaction, member: discord.Member):
        verb = random.choice(self.verbs)
        action = random.choice(self.hello_variable)
        await self._execute_action(
            interaction=interaction,
            member=member,
            gifs_key="hello_gifs",
            color=0xE3D53B,
            title=f"{self.hello_em} ᴨᴩиʙᴇᴛᴄᴛʙиᴇ!",
            action_verb=f"{verb} {action}",
            self_error=f"{self.dn_em} ᴨᴩоᴄᴛиᴛᴇ, ʙы нᴇ ʍожᴇᴛᴇ ᴨоᴨᴩиʙᴇᴛᴄᴛоʙᴀᴛь ᴄᴀʍоᴦо ᴄᴇбя!"
        )

    # COMMAND: Команда интерактивного действия "обнять"
    @app_commands.command(name="обнять", description="Обнять пользователя.")
    @app_commands.describe(member="Пользователя, которого хотите обнять.")
    @app_commands.guild_only()
    async def hug_command(self, interaction: discord.Interaction, member: discord.Member):
        verb = random.choice(self.verbs)
        action = random.choice(self.hug_variable)
        await self._execute_action(
            interaction=interaction,
            member=member,
            gifs_key="hug_gifs",
            color=0x9B4AA1,
            title=f"{self.hug_em} обниʍᴀɯᴋи!",
            action_verb=f"{verb} {action}",
            self_error=f"{self.dn_em} ᴨᴩоᴄᴛиᴛᴇ, ʙы нᴇ ʍожᴇᴛᴇ обняᴛь ᴄᴀʍоᴦо ᴄᴇбя!"
        )

    # COMMAND: Команда интерактивного действия "поцеловать"
    @app_commands.command(name="поцеловать", description="Поцеловать пользователя.")
    @app_commands.describe(member="Пользователя, которого хотите поцеловать.")
    @app_commands.guild_only()
    async def kiss_command(self, interaction: discord.Interaction, member: discord.Member):
        verb = random.choice(self.verbs)
        action = random.choice(self.kiss_variable)
        await self._execute_action(
            interaction=interaction,
            member=member,
            gifs_key="kiss_gifs",
            color=0xA83439,
            title=f"{self.kiss_em} ᴨоцᴇᴧуйчиᴋи!",
            action_verb=f"{verb} {action}",
            self_error=f"{self.dn_em} ᴨᴩоᴄᴛиᴛᴇ, ʙы нᴇ ʍожᴇᴛᴇ ᴨоцᴇᴧоʙᴀᴛь ᴄᴀʍоᴦо ᴄᴇбя!"
        )

    # COMMAND: Команда интерактивного действия "погладить"
    @app_commands.command(name="погладить", description="Погладить пользователя.")
    @app_commands.describe(member="Пользователя, которого хотите погладить.")
    @app_commands.guild_only()
    async def pat_command(self, interaction: discord.Interaction, member: discord.Member):
        verb = random.choice(self.verbs)
        action = random.choice(self.pat_variable)
        await self._execute_action(
            interaction=interaction,
            member=member,
            gifs_key="pat_gifs",
            color=0x814B8B,
            title=f"{self.pat_em} ʍиᴧᴀɯᴋи!",
            action_verb=f"{verb} {action}",
            self_error=f"{self.dn_em} ᴨᴩоᴄᴛиᴛᴇ, ʙы нᴇ ʍожᴇᴛᴇ ᴨоᴦᴧᴀдиᴛь ᴄᴀʍоᴦо ᴄᴇбя!"
        )

    # COMMAND: Команда интерактивного действия "укусить"
    @app_commands.command(name="укусить", description="Укусить пользователя.")
    @app_commands.describe(member="Пользователя, которого хотите укусить.")
    @app_commands.guild_only()
    async def bite_command(self, interaction: discord.Interaction, member: discord.Member):
        verb = random.choice(self.verbs)
        action = random.choice(self.bite_variable)
        await self._execute_action(
            interaction=interaction,
            member=member,
            gifs_key="bite_gifs",
            color=0x781111,
            title=f"{self.bite_em} ʙᴀʍᴨиᴩчиᴋи!",
            action_verb=f"{verb} {action}",
            self_error=f"{self.dn_em} ᴨᴩоᴄᴛиᴛᴇ, ʙы нᴇ ʍожᴇᴛᴇ уᴋуᴄиᴛь ᴄᴀʍоᴦо ᴄᴇбя!"
        )

    # COMMAND: Команда интерактивного действия "убить"
    @app_commands.command(name="убить", description="Ранить пользователя. (РП действие)")
    @app_commands.describe(member="Пользователя, которого хотите ранить. (РП действие)")
    @app_commands.guild_only()
    async def kill_command(self, interaction: discord.Interaction, member: discord.Member):
        action = random.choice(self.kill_variable)
        await self._execute_action(
            interaction=interaction,
            member=member,
            gifs_key="kill_gifs",
            color=0x787373,
            title=f"{self.kill_em} ʙойнуɯᴋи!",
            action_verb=f"ᴨо-дᴩужᴇᴄᴋи {action}",
            self_error=f"{self.dn_em} ᴨᴩоᴄᴛиᴛᴇ, ʙы нᴇ ʍожᴇᴛᴇ ᴩᴀниᴛь ᴄᴀʍоᴦо ᴄᴇбя!"
        )

    # COMMAND: Команда интерактивного действия "развлечься"
    @app_commands.command(name="развлечься", description="Развлечь пользователя. (РП действие)")
    @app_commands.describe(member="Пользователя, которого хотите развеселить. (РП действие)")
    @app_commands.guild_only()
    async def secret_command(self, interaction: discord.Interaction, member: discord.Member):
        action = random.choice(self.secret_variable)
        gif = random.choice(secret_gifs)

        # LOGIC: Создаём файл
        file = discord.File(
            gif,
            filename="interaction.gif",
        )

        # LOGIC: Передаем файл и переменную secret
        await self._execute_action(
            interaction=interaction,
            member=member,
            gifs_key=f"attachment://interaction.gif",
            color=0xF18E8E,
            title=f"{self.secret_em} ᴩᴀзʙᴧᴇᴋуɯᴋи!",
            action_verb=f"ᴨо-дᴩужᴇᴄᴋи {action}",
            self_error=f"{self.dn_em} ᴨᴩоᴄᴛиᴛᴇ, ʙы нᴇ ʍожᴇᴛᴇ ᴩᴀзʙᴧᴇчь ᴄᴀʍоᴦо ᴄᴇбя!",
            downloaded=True,
            file=file
        )

# LOGIC: Запуск кога
async def setup(bot):
    await bot.add_cog(RoleplayCog(bot))