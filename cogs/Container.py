import discord, time, random
from discord import app_commands
from pathlib import Path
from discord.ext import commands, tasks

# Импорт ваших собственных настроек и функций из корня проекта
from config import BotConfig
from database.db_logic import DB_Manager

BASE_DIR = Path(__file__).parent

# LOGIC: Выбор способа открытия саркофага
class SarcophagusSelect(discord.ui.Select):
    def __init__(self, cog, view):
        self.cog = cog
        self.sarcophagus_view = view

        # VARIABLE: Эмодзи для сообщений
        self.vl_em = "<:value_emoji:1553133311365349457>"
        self.gr_em = "<a:alright_emoji:1552752070262521917>"
        self.dn_em = "<a:denied_emoji:1552780290609512658>"
        self.ow_em = "<a:owner_emoji:1552781248236097546>"
        self.at_em = "<a:attention_emoji:1552749665030508654>"
        self.p_vl_em = discord.PartialEmoji(name="value_emoji", id=1553133311365349457)

        self.options_data = {
            "crowbar": {
                "chance": 90,
                "reward_min": 10,
                "reward_max": 25,
                "success_text": "ᴄ ᴧᴇᴦᴋоᴄᴛью ʙᴄᴋᴩыᴧ ᴧоʍоʍ",
                "fail_text": "нᴇ ʙозʍожно ʙᴄᴋᴩыᴛь ᴧоʍоʍ"
            },
            "grinder": {
                "chance": 45,
                "reward_min": 30,
                "reward_max": 45,
                "success_text": "ᴀᴋᴋуᴩᴀᴛно ʙᴄᴋᴩыᴧ боᴧᴦᴀᴩᴋой",
                "fail_text": "оᴋᴀзᴀᴧᴄя ᴄᴧиɯᴋоʍ ᴛʙᴇᴩд дᴧя боᴧᴦᴀᴩᴋи"
            },
            "explosive": {
                "chance": 15,
                "reward_min": 55,
                "reward_max": 85,
                "success_text": "удᴀчно ʙзоᴩʙᴀᴧ ᴛᴩᴀᴛиᴧоʍ",
                "fail_text": "быᴧ ʙзоᴩʙᴀн ᴄ ʙнуᴛᴩᴇнниʍ ᴄодᴇᴩжиʍыʍ"
            },
        }

        super().__init__(
            custom_id="sarcophagus_select",
            placeholder="ʙыбᴇᴩиᴛᴇ дᴇйᴄᴛʙиᴇ, ʙниʍᴀниᴇ нᴀ % уᴄᴨᴇхᴀ.",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(
                    label=(
                        f"ʙᴄᴋᴩыᴛь ᴧоʍоʍ "
                        f"{self.options_data['crowbar']['chance']}% "
                        f"=> {self.options_data['crowbar']['reward_min']}-"
                        f"{self.options_data['crowbar']['reward_max']}"
                    ),
                    emoji=self.p_vl_em,
                    value="crowbar",
                ),
                discord.SelectOption(
                    label=(
                        f"ʙᴄᴋᴩыᴛь боᴧᴦᴀᴩᴋой "
                        f"{self.options_data['grinder']['chance']}% "
                        f"=> {self.options_data['grinder']['reward_min']}-"
                        f"{self.options_data['grinder']['reward_max']}"
                    ),
                    emoji=self.p_vl_em,
                    value="grinder",
                ),
                discord.SelectOption(
                    label=(
                        f"ʙᴄᴋᴩыᴛь ʙзᴩыʙчᴀᴛᴋой "
                        f"{self.options_data['explosive']['chance']}% "
                        f"=> {self.options_data['explosive']['reward_min']}-"
                        f"{self.options_data['explosive']['reward_max']}"
                    ),
                    emoji=self.p_vl_em,
                    value="explosive",
                ),
            ],
        )

    async def callback(self, interaction: discord.Interaction):

        selected = self.values[0]
        data = self.options_data[selected]

        user = interaction.user

        # Проверяем шанс
        success = random.randint(1, 100) <= data["chance"]
        if success:
            reward = random.randint(
                data["reward_min"],
                data["reward_max"],
            )

            user_data = await self.cog.manager.get_user_economic(
                user.id
            )

            new_points = user_data["points"] + reward

            await self.cog.manager.update_user_economic(
                user.id,
                new_points,
                user_data["last_claim"],
                user_data["last_water"],
                user_data["last_collect"],
                user_data["last_fish"],
                user_data["last_bonus"],
                user_data["last_rob"],
            )

            success_text = data["success_text"]

            content = (
                f"### бᴧᴀᴦоᴄᴧᴀʙᴇниᴇ ᴄᴀᴩᴋоɸᴀᴦᴀ {self.gr_em}\n"
                f"{self.at_em} "
                f"{user.mention} **{success_text}** ᴄᴀᴩᴋоɸᴀᴦ!\n"
                f"{self.at_em} ᴨоᴧучᴇнноᴇ ʙознᴀᴦᴩᴀждᴇниᴇ: `{reward}` "
                f"{self.vl_em}."
                f"\n\n-# {self.ow_em} ᴄᴧᴇдующᴇй ᴄᴀᴩᴋоɸᴀᴦ ᴨояʙиᴛᴄя чᴇᴩᴇз нᴇᴋоᴛоᴩоᴇ ʙᴩᴇʍя, ʙᴋᴧючиᴛᴇ уʙᴇдоʍᴧᴇния."
            )

        else:
            fail_text = data["fail_text"]

            content = (
                f"### ᴨᴩоᴋᴧяᴛиᴇ ᴄᴀᴩᴋоɸᴀᴦᴀ {self.dn_em}\n"
                f"{self.at_em} "
                f"{user.mention} ᴨᴩоизʙᴇᴧ нᴇудᴀчную ᴨоᴨыᴛᴋу оᴛᴋᴩыᴛия!\n"
                f"{self.at_em} ᴄᴀᴩᴋоɸᴀᴦ **{fail_text}**."
                f"\n\n-# {self.ow_em} ᴄᴧᴇдующᴇй ᴄᴀᴩᴋоɸᴀᴦ ᴨояʙиᴛᴄя чᴇᴩᴇз нᴇᴋоᴛоᴩоᴇ ʙᴩᴇʍя, ʙᴋᴧючиᴛᴇ уʙᴇдоʍᴧᴇния."
            )

        await self.cog.manager.update_count_containers(
                user.id
            )

        view = DefaultComponent(content=content, interaction=interaction, is_timeout=False)

        self.disabled = True

        await interaction.response.edit_message(
            view=view
        )

        self.sarcophagus_view.stop()

# COMPANENT: Компанент простого текстового сообщения
class DefaultComponent(discord.ui.LayoutView):
    def __init__(
        self,
        content,
        interaction=None,
        is_timeout=False
    ):
        super().__init__()

        avatar_url = None
        if interaction != None:
            user = interaction.user
            avatar_url = user.display_avatar.url

        self.InfoContainer = None
        if is_timeout:
            self.InfoContainer = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=content,
                ),
            )

        else:
            self.InfoContainer = discord.ui.Container(
                discord.ui.Section(
                    discord.ui.TextDisplay(
                        content=content,
                    ),
                    accessory=discord.ui.Thumbnail(
                        avatar_url
                    ),
                ),
            )
        
        self.add_item(self.InfoContainer)

# COMPANENT: Компанент основого контейнера
class SarcophagusComponent(discord.ui.LayoutView):
    def __init__(
        self,
        cog
    ):
        super().__init__(timeout=1800)

        self.cog = cog
        self.message = None

        # VARIABLE: Эмодзи для сообщений
        self.ts_em = "<a:tombstone_emoji:1553765267979636766>"
        self.dn_em = "<a:denied_emoji:1552780290609512658>"
        self.ow_em = "<a:owner_emoji:1552781248236097546>"

        self.InfoContainer = discord.ui.Container(
            discord.ui.TextDisplay(
                content=(
                    f"# ᴛᴀинᴄᴛʙᴇнный ᴄᴀᴩᴋоɸᴀᴦ {self.ts_em}\n"
                    "-# ᴨᴩоходя ᴨо ᴋᴧᴀдбищу, ʙы зᴀʍᴇчᴀᴇᴛᴇ "
                    "оᴄобый ᴄᴀᴩᴋоɸᴀᴦ (ᴦᴩоб) ᴄ ᴛᴀинᴄᴛʙᴇнной "
                    "ᴨᴩиᴨиᴄᴋой ʜᴏᴘᴇ... иᴄᴨыᴛᴀйᴛᴇ удᴀчу ʙ ᴇᴦо оᴛᴋᴩыᴛии. ||@here||"
                ),
            ),

            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    "attachment://sarcophagus.jpg",
                    description="Изображение саркофага",
                ),
            ),

            discord.ui.Separator(
                visible=True,
                spacing=discord.SeparatorSpacing.large,
            ),

            discord.ui.TextDisplay(
                content=(
                    "**ʙᴀɯи дᴀᴧьнᴇйɯиᴇ дᴇйᴄᴛʙия:**\n"
                    "- пройти мимо, упустив возможный улов.\n"
                    "- успеть открыть саркофаг быстрее остальных."
                ),
            ),

            discord.ui.TextDisplay(
                content=(
                    "ᴨоᴋᴀ ʙы ʍᴇдᴧиᴛᴇ, оᴄᴛᴀᴧьныᴇ ужᴇ "
                    "ᴦоᴛоʙяᴛᴄя ᴋ ʙᴄᴋᴩыᴛию ᴄᴀᴩᴋоɸᴀᴦᴀ!"
                ),
            ),

            discord.ui.ActionRow(
                SarcophagusSelect(
                    cog=cog,
                    view=self
                ),
            ),
        )

        self.add_item(self.InfoContainer)

    async def on_timeout(self):
        # Отключаем Select
        for item in self.walk_children():
            if isinstance(item, discord.ui.Select):
                item.disabled = True

        if self.message:
            try:
                content = f"{self.dn_em} ᴄᴩоᴋ ᴦодноᴄᴛи ᴄᴀᴩᴋоɸᴀᴦᴀ иᴄчᴇᴩᴨᴀны...\n{self.dn_em} дᴀнноᴇ ᴄобыᴛиᴇ нᴇ доᴄᴛуᴨно.\n\n-# {self.ow_em} ᴄᴧᴇдующᴇй ᴄᴀᴩᴋоɸᴀᴦ ᴨояʙиᴛᴄя чᴇᴩᴇз нᴇᴋоᴛоᴩоᴇ ʙᴩᴇʍя, ʙᴋᴧючиᴛᴇ уʙᴇдоʍᴧᴇния."
                view = DefaultComponent(content=content, interaction=None, is_timeout=True)
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

class ContainerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.manager = DB_Manager(BotConfig.DB_PATH)

        self.container_loop.start()

    def cog_unload(self):
        self.container_loop.cancel()

    @tasks.loop(hours=6)
    async def container_loop(self):
        if not BotConfig.TRANSACTIONS_AVAILABLE:
            return

        channel = self.bot.get_channel(
            BotConfig.COMMAND_CHANNEL
        )

        if channel is None:
            return
        
        image_path = BASE_DIR.parent / "references" / "images" / "sarcophagus.jpg"

        file = discord.File(
            image_path,
            filename="sarcophagus.jpg"
        )

        try:
            view = SarcophagusComponent(
                cog=self
            )

            message = await channel.send(file=file, view=view)

            view.message = message

        except Exception as e:
            print(
                f"❌ Не удалось отправить сообщение пользователю: "
                f"{type(e).__name__}: {e}"
            )

    @container_loop.before_loop
    async def before_container_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(ContainerCog(bot))