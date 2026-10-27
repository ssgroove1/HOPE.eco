import discord, time, random, sqlite3
from discord import app_commands
from pathlib import Path
from discord.ext import commands, tasks

from config import BotConfig
from database.db_logic import DB_Manager

# LOGIC: Выбор роли из магазина ролей
class RoleShopSelect(discord.ui.Select):
    def __init__(self, cog, options):
        self.cog = cog

        # LOGIC: Инициализация селекта с опциями ролей
        super().__init__(
            custom_id="role_shop_select",
            placeholder="ʙыбᴇᴩиᴛᴇ ᴩоᴧь дᴧя ᴨоᴋуᴨᴋи",
            min_values=1,
            max_values=1,
            options=options,
        )

    # METHOD: Обработка выбора роли
    async def callback(self, interaction: discord.Interaction):
        # LOGIC: Получаем роль по выбранному значению
        role_id = int(self.values[0])
        role = interaction.guild.get_role(role_id)

        # LOGIC: Всевозможные проверки перед покупкой роли
        if role is None:
            msg = (
                f"{self.cog.dn_em} ᴩоᴧь нᴇ нᴀйдᴇнᴀ нᴀ сᴇᴩʙᴇᴩᴇ."
                f"\n\n{self.cog.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, нᴀᴨиɯиᴛᴇ ᴄоздᴀᴛᴇᴧю."
            )
            await self.cog.send_message(
                interaction,
                msg,
                True
            )
            return

        if role in interaction.user.roles:
            msg = (
                f"{self.cog.dn_em} ϶ᴛᴀ ᴩоᴧь ужᴇ у ʙᴀᴄ ᴨᴩиобᴩᴇᴛᴇнᴀ."
                f"\n\n{self.cog.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, нᴀᴨиɯиᴛᴇ ᴄоздᴀᴛᴇᴧю."
            )
            await self.cog.send_message(
                interaction,
                msg,
                True
            )
            return

        # LOGIC: Пытаемся купить роль через менеджер базы данных
        result = await self.cog.manager.buy_shop_role(
            interaction.user.id,
            role.id
        )

        # LOGIC: Обработка результата покупки роли
        if not result["success"]:
            msg = None
            if result["reason"] == "not_enough_points":
                price = result["price"]
                points = result["points"]

                msg = (
                    f"{self.cog.dn_em} нᴇдоᴄᴛᴀᴛочно ʙᴀᴧюᴛы дᴧя ᴨоᴋуᴨᴋи.\n"
                    f"{self.cog.dn_em} ᴄᴛоиʍоᴄᴛь ᴩоᴧи: `{price}` {self.cog.vl_em}\n"
                    f"{self.cog.dn_em} ʙᴀɯ бᴀᴧᴀнᴄ: `{points}` {self.cog.vl_em}"
                    f"\n\n{self.cog.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, нᴀᴨиɯиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )
            elif result["reason"] == "role_not_found":
                msg = (
                    f"{self.cog.dn_em} ᴩоᴧь бoᴧьɯᴇ нᴇдоступнᴀ ʙ ʍᴀᴦᴀзинᴇ."
                    f"\n\n{self.cog.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, нᴀᴨиɯиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )
            else:
                msg = (
                    f"{self.cog.dn_em} ᴨᴩи ᴨоᴋуᴨᴋᴇ ᴨᴩоизоɯᴧᴀ оɯибᴋᴀ."
                    f"\n\n{self.cog.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, нᴀᴨиɯиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )

            await self.cog.send_message(
                interaction,
                msg,
                True
            )
            return

        # METHOD: Подтверждение покупки роли
        async def confirm_action(confirm_interaction: discord.Interaction):
            # LOGIC: Данные успешной покупки
            points_spent = result["points_spent"]
            new_points = result["new_points"]

            # LOGIC: Пытаемся выдать роль пользователю
            try:
                await interaction.user.add_roles(
                    role,
                    reason="Покупка роли в магазине"
                )

                # LOGIC: Успешная покупка
                msg = (
                    f"{self.cog.gr_em} ʙы, {confirm_interaction.user.mention}, уᴄᴨᴇɯно ᴨᴩиобᴩᴇᴧи ᴩоᴧь {role.mention}.\n"
                    f"{self.cog.gr_em} ᴄо ᴄчᴇᴛᴀ ᴄᴨиᴄᴀно: `{points_spent}` {self.cog.vl_em}\n"
                    f"{self.cog.gr_em} оᴄᴛᴀᴧоᴄь нᴀ ᴄчᴇᴛᴇ: `{new_points}` {self.cog.vl_em}"
                    f"\n\n{self.cog.ow_em} ᴨоздᴩᴀʙᴧяᴇʍ ʙᴀᴄ ᴄ ᴨоᴋуᴨᴋой!."
                )
                await self.cog.send_message(
                    interaction,
                    msg
                )

            # LOGIC: Возвращение потраченных денег в случае ошибки выдачи роли
            except discord.Forbidden:
                await self.cog.manager.add_points(
                    interaction.user.id,
                    points_spent
                )

                e_msg = (
                    f"{self.cog.dn_em} нᴇ удᴀᴧоᴄь ʙыдᴀᴛь ʙᴀʍ ᴩоᴧь.\n"
                    f"{self.cog.dn_em} ʙᴀᴧюᴛᴀ ʙᴇᴩнулᴀᴄь нᴀ ᴄчᴇᴛ: "
                    f"`{points_spent}` {self.cog.vl_em}"
                    f"\n\n{self.cog.ow_em} ᴨᴩᴏʙᴇᴩьᴛᴇ, чᴛо ᴩоᴧь боᴛᴀ ᴄᴛоиᴛ ʙыɯᴇ ᴩоᴧи."
                )
                await self.cog.send_message(
                    interaction,
                    e_msg,
                    True
                )
    
            except discord.HTTPException as error:
                await self.cog.manager.add_points(
                    interaction.user.id,
                    points_spent
                )
    
                print(
                    f"❌ Ошибка при выдаче роли: "
                    f"{type(error).__name__}: {error}"
                )

                e_msg = (
                    f"{self.cog.dn_em} ᴨᴩи ʙыдᴀчᴇ ᴩоᴧи ᴨᴩоизоɯᴧᴀ оɯибᴋᴀ.\n"
                    f"{self.cog.dn_em} ʙᴀᴧюᴛᴀ ʙᴇᴩнулᴀᴄь нᴀ ᴄчᴇᴛ: "
                    f"`{points_spent}` {self.cog.vl_em}"
                    f"\n\n{self.cog.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, нᴀᴨиɯиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )
                await self.cog.send_message(
                    interaction,
                    e_msg,
                    True
                )

            except Exception as error:
                print(
                    f"❌ Непредвиденная ошибка при покупке роли: "
                    f"{type(error).__name__}: {error}"
                )

                try:
                    await self.cog.manager.add_points(
                        confirm_interaction.user.id,
                        points_spent
                    )
                except Exception as refund_error:
                    print(
                        f"❌ Не удалось вернуть валюту пользователю: "
                        f"{type(refund_error).__name__}: {refund_error}"
                    )

                e_msg = (
                    f"{self.cog.dn_em} ᴨᴩи ᴨᴩиобᴩᴇᴛᴇнии ᴩоᴧи ᴨᴩᴏизоɯᴧᴀ "
                    f"нᴇᴨᴩᴇдʙидᴇннᴀя оɯибᴋᴀ.\n"
                    f"{self.cog.dn_em} ʙᴀᴧюᴛᴀ ʙᴇᴩнулᴀᴄь нᴀ ᴄчᴇᴛ: "
                    f"`{points_spent}` {self.cog.vl_em}"
                    f"\n\n{self.cog.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, нᴀᴨиɯиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )

                try:
                    await self.cog.send_message(
                        confirm_interaction,
                        e_msg,
                        True
                    )
                except Exception as send_error:
                    print(
                        f"❌ Не удалось отправить сообщение об ошибке: "
                        f"{type(send_error).__name__}: {send_error}"
                    )

        # LOGIC: Сообщение подверждения
        view = ConfirmComponent(
            on_confirm=confirm_action,
            is_admin=False
        )

        await interaction.response.send_message(
            view=view,
            ephemeral=True
        )

        view.message = await interaction.original_response()

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

# COMPANENT: Компанент подверждения действия
class ConfirmComponent(discord.ui.LayoutView):
    def __init__(
        self,
        on_confirm = None,
        is_admin = False
    ):
        super().__init__(timeout=60)

        self.message = None
        self.on_confirm = on_confirm

        # VARIABLE: Эмодзи для сообщений
        ow_em = "<a:owner_emoji:1552781248236097546>"
        at_em = "<a:attention_emoji:1552749665030508654>"

        # LOGIC: Создаем кнопки подтверждения и отмены
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

        self.confirm_button.callback = self.confirm
        self.cancel_button.callback = self.cancel

        self.InfoContainer = None
        # LOGIC: Логика отображения текста в зависимости от того, является ли пользователь администратором
        if is_admin:
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
        else:
            self.InfoContainer = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=(
                        f"{at_em} ᴦоᴛоʙы ᴧи ʙы ᴨоᴛᴩᴀᴛиᴛь ᴄʙою ʙᴀᴧюᴛу нᴀ ᴩоᴧь?\n"
                        f"{at_em} обᴩᴀᴛиᴛь ϶ᴛо дᴇйᴄᴛʙиᴇ ужᴇ нᴇᴧьзя будᴇᴛ.\n"
                        f"{at_em} будᴇᴛ оᴛᴋᴧонᴇно ᴨоᴄᴧᴇ 60 ᴄᴇᴋунд бᴇздᴇйᴄᴛʙия.\n"
                        f"\n-# {ow_em} ʙ ᴄᴧучᴀᴇ нᴇᴋоᴩᴩᴇᴋᴛноᴦо ᴄᴩᴀбᴀᴛыʙᴀния, нᴀᴨиɯиᴛᴇ ᴄоздᴀᴛᴇᴧю."
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

    # METHOD: Отключение кнопок
    async def disable_buttons(self):
        self.confirm_button.disabled = True
        self.cancel_button.disabled = True

    # METHOD: Обработка нажатия кнопок: подтверждение действия
    async def confirm(self, interaction: discord.Interaction):
        await self.disable_buttons()
        await interaction.response.edit_message(view=self)
        await self.on_confirm(interaction)
        self.stop()

    # METHOD: Обработка нажатия кнопок: отмена действия
    async def cancel(self, interaction: discord.Interaction):
        await self.disable_buttons()
        await interaction.response.edit_message(view=self)
        self.stop()

    # METHOD: Обработка таймаута (60 секунд)
    async def on_timeout(self):
        await self.disable_buttons()

        if self.message:
            await self.message.edit(
                view=self
            )

# COMPANENT: Компанент магазина ролей
class RoleShopComponent(discord.ui.LayoutView):
    # LOGIC: Получение ролей для магазина
    @classmethod
    async def create(cls, guild, cog):
        roles = await cog.manager.get_shop_roles()
        # LOGIC: Передаем полученные роли в конструктор класса RoleShopComponent
        return cls(
            guild=guild,
            cog=cog,
            roles=roles
        )
    # LOGIC: Инициализация компонента магазина ролей
    def __init__(self, guild, cog, roles):
        super().__init__(timeout=300)
        self.cog = cog
        self.message = None

        guild_name = guild.name
        guild_icon = (
            guild.icon.url
            if guild.icon
            else "https://dweeb.faizo.net/media/defaults/dweeb-default-thumbnail.jpg"
        )

        # LOGIC: Опция выбора ролей для магазина
        options = []

        if roles:
            for role_id, price in roles:
                role = guild.get_role(role_id)

                if role is None:
                    continue

                options.append(
                    discord.SelectOption(
                        label=role.name[:100],
                        description=f"Стоимость: {price}",
                        value=str(role.id),
                    )
                )

        # LOGIC: Создаем контейнер с информацией о магазине ролей
        self.InfoContainer = None
        if not options: # LOGIC: Если нет доступных ролей для покупки, отображаем соответствующее сообщение
            self.InfoContainer = discord.ui.Container(
                discord.ui.TextDisplay(
                    content=(
                        f"# ᴧᴀʙᴋᴀ ᴩоᴧᴇй {self.cog.sp_em}\n"
                        f"-# ʙ дᴀнный ʍоʍᴇнᴛ ʙ ᴧᴀʙᴋᴇ нᴇᴛ доступных ролей."
                    )
                )
            )
        else:
            self.InfoContainer = discord.ui.Container(
                discord.ui.Section(
                    discord.ui.TextDisplay(
                        content=(
                            f"# ᴧᴀʙᴋᴀ ᴨоᴋуᴨᴋи ᴩоᴧᴇй {self.cog.sp_em}\n"
                            f"-# ᴨᴩиᴧᴀʙоᴋ дᴧя ᴨоᴋуᴨᴋи ᴩоᴧᴇй "
                            f"зᴀ ʙнуᴛᴩи доступную валюту сервера, "
                            f"**{guild_name}**."
                        ),
                    ),
                    accessory=discord.ui.Thumbnail(
                        guild_icon,
                        description="server_icon",
                    ),
                ),

                discord.ui.Separator(
                    visible=True,
                    spacing=discord.SeparatorSpacing.large,
                ),

                discord.ui.TextDisplay(
                    content=(
                        "**дᴧя ᴨᴩиобᴩᴇᴛᴇния ᴩоᴧи:**\n"
                        "- выберите роль снизу.\n"
                        "- оцените ваши доходы и её стоимость.\n"
                        "- купите выбранную вами роль."
                    ),
                ),

                discord.ui.ActionRow(
                    RoleShopSelect(
                        cog=self.cog,
                        options=options,
                    )
                ),

                discord.ui.TextDisplay(
                    content=f"-# {self.cog.ow_em} ᴧᴀʙᴋᴀ ᴩᴀбоᴛᴀᴇᴛ нᴇᴋоᴩᴩᴇᴋᴛно, нᴀᴨиɯиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                ),
            )

        self.add_item(self.InfoContainer)

    # METHOD: Обработка таймаута (5 минут)
    async def on_timeout(self):
        for item in self.walk_children():
            if isinstance(item, discord.ui.Select):
                item.disabled = True
        if self.message is None:
            return
        try:
            content = (
                f"{self.cog.dn_em} ᴧᴀᴩᴇᴋ быᴧ зᴀᴋᴩыᴛ, "
                f"ʙʙᴇдиᴛᴇ ᴋоʍᴀнду ᴄноʙᴀ.\n\n"
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

# LOGIC: Основной функционал обработки магазина
class ShopCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.manager = DB_Manager(BotConfig.DB_PATH)

        # VARIABLE: Эмодзи для сообщений
        self.vl_em = "<:value_emoji:1553133311365349457>"
        self.dn_em = "<a:denied_emoji:1552780290609512658>"
        self.gr_em = "<a:alright_emoji:1552752070262521917>"
        self.wt_em = "<a:wait_emoji:1552785236549443634>"
        self.ow_em = "<a:owner_emoji:1552781248236097546>"
        self.sp_em = "<a:shop_emoji:1554944276625105026>"
        self.at_em = "<a:attention_emoji:1552749665030508654>"

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

    # COMMAND: Открытие магазина ролей
    @app_commands.command(name="магазин", description="Открыть магазин.")
    @app_commands.guild_only()
    async def shop_command(self, interaction: discord.Interaction):
        if not await self.command_checks(interaction):
            return

        try:
            guild = interaction.guild

            view = await RoleShopComponent.create(
                guild=guild,
                cog=self
            )

            if interaction.response.is_done():
                await interaction.followup.send(
                    view=view,
                    ephemeral=False
                )
            else:
                await interaction.response.send_message(
                    view=view,
                    ephemeral=False
                )

            view.message = await interaction.original_response()

        except Exception as e:
            print(
                f"❌ Не удалось открыть магазин: "
                f"{type(e).__name__}: {e}"
            )

    # COMMAND: Добавление товара в магазин
    @app_commands.command(name="добавить_товар", description="Добавить товар для магазина.")
    @app_commands.describe(role="Роль для продажи.", price="Стоимость роли.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    async def add_item_command(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
        price: int,
    ):
        # LOGIC: Проверяем возможность добавления роли в магазин
        try:
            # LOGIC: Проверяем, что роль существует
            if role is None:
                msg = (
                    f"{self.dn_em} ᴩоᴧь нᴇ нᴀйдᴇнᴀ. ʙыбᴇᴩиᴛᴇ дᴩуᴦую ᴩоᴧь.\n"
                    f"\n\n-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴨиɯиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )
                await self.send_message(
                    interaction,
                    msg,
                    True
                )
                return

            # LOGIC: Проверяем @everyone
            if role.is_default():
                msg = (
                    f"{self.dn_em} ᴩоᴧь @everyone нᴇᴧьзя добᴀʙиᴛь ʙ ʍᴀᴦᴀзин."
                    f"\n\n-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴨиɯиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )
                await self.send_message(
                    interaction,
                    msg,
                    True
                )
                return

            # LOGIC: Проверяем managed-роль
            if role.managed:
                msg = (
                    f"{self.dn_em} ϶ᴛу ᴩоᴧь нᴇᴧьзя иᴄᴨоᴧьзоʙᴀᴛь ᴄᴇйчᴀᴄ.\n"
                    f"{self.dn_em} ᴩоᴧь уᴨᴩᴀʙᴧяᴇᴛᴄя дᴩуᴦиʍ боᴛоʍ."
                    f"\n\n-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴨиɯиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )
                await self.send_message(
                    interaction,
                    msg,
                    True
                )
                return

            # LOGIC: Получаем участника-бота
            bot_member = interaction.guild.me

            if bot_member is None:
                msg =(
                    f"{self.dn_em} нᴇ удᴀᴧоᴄь ᴨоᴧучить дᴀнныᴇ о бoᴛᴇ.\n"
                    f"{self.dn_em} ʙозʍожно боᴛᴀ боᴧьɯᴇ нᴇᴛу нᴀ ᴄᴇᴩʙᴇᴩᴇ."
                    f"\n\n-# {self.ow_em} ᴄоздᴀᴛᴇᴧь боᴛᴀ оᴄʙᴇдоʍᴧᴇн об ϶ᴛоʍ."
                )
                await self.send_message(
                    interaction,
                    msg,
                    True
                )
                return

            # LOGIC: Проверяем, сможет ли бот выдать эту роль
            if role >= bot_member.top_role:
                msg = (
                    f"{self.dn_em} бoᴛ нᴇ ʍожᴇᴛ ʙыдᴀᴛь ᴩоᴧь {role.mention}.\n"
                    f"{self.dn_em} ᴨᴇᴩᴇʍᴇᴄᴛиᴛᴇ ᴩоᴧь бoᴛᴀ ʙыɯᴇ ϶ᴛой ᴩоᴧи."
                    f"\n\n-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴨиɯиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )
                await self.send_message(
                    interaction,
                    msg,
                    True
                )
                return

            # LOGIC: Проверяем ID роли
            if not isinstance(role.id, int):
                msg = (
                    f"{self.dn_em} ᴨᴩоизоɯᴧᴀ оɯибᴋᴀ ᴨᴩи ᴨᴩᴏʙᴇᴩᴋᴇ ᴩоᴧи."
                    f"\n\n-# {self.ow_em} ᴄоздᴀᴛᴇᴧь боᴛᴀ оᴄʙᴇдоʍᴧᴇн об ϶ᴛоʍ."
                )
                await self.send_message(
                    interaction,
                    msg,
                    True
                )
                return

            # LOGIC: Проверяем цену
            if price <= 0:
                msg = (
                    f"{self.dn_em} ᴄᴛоиʍоᴄᴛь ᴩоᴧи дᴏᴧжнᴀ быть ʙыɯᴇ нуᴧя."
                    f"\n\n-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴨиɯиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )
                await self.send_message(
                    interaction,
                    msg,
                    True
                )
                return

            # LOGIC: Проверяем максимальную стоимость
            if price > 100_000:
                msg = (
                    f"{self.dn_em} мᴀᴋᴄиʍᴀᴧьнᴀя ᴄᴛоиʍоᴄᴛь ᴩоᴧи — `100 000` "
                    f"{self.vl_em}."
                    f"\n\n-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴨиɯиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )
                await self.send_message(
                    interaction,
                    msg,
                    True
                )
                return

            # LOGIC: Проверяем магазин в БД
            result = await self.manager.can_add_shop_role(role.id)

            # LOGIC: Проверяем, что БД вернула ожидаемый результат
            if result not in ("success", "limit", "exists"):
                print(
                    f"❌ Неизвестный результат can_add_shop_role: "
                    f"{result!r}"
                )

                msg = (
                    f"{self.dn_em} ᴨᴩоизоɯᴧᴀ оɯибᴋᴀ ᴨᴩи ᴨᴩᴏʙᴇᴩᴋᴇ ᴩоᴧи."
                    f"\n\n-# {self.ow_em} ᴄоздᴀᴛᴇᴧь боᴛᴀ оᴄʙᴇдоʍᴧᴇн об ϶ᴛоʍ."
                )

                await self.send_message(
                    interaction,
                    msg,
                    True
                )
                return

            # LOGIC: Магазин уже содержит 25 ролей
            if result == "limit":
                e_msg = (
                    f"{self.dn_em} ʙ ʍᴀᴦᴀзинᴇ ужᴇ нᴀходиᴛᴄя 25 ᴩоᴧᴇй.\n"
                    f"{self.dn_em} ᴄнᴀчᴀᴧᴀ удᴀᴧиᴛᴇ одну из ᴩоᴧᴇй."
                    f"\n\n-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴨиɯиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )

                await self.send_message(
                    interaction,
                    e_msg,
                    True
                )
                return

            # LOGIC: Роль уже находится в магазине
            if result == "exists":
                e_msg = (
                    f"{self.dn_em} ᴩоᴧь {role.mention} ужᴇ нᴀходиᴛᴄя ʙ ʍᴀᴦᴀзинᴇ."
                    f"\n\n-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴨиɯиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )

                await self.send_message(
                    interaction,
                    e_msg,
                    True
                )
                return

        # LOGIC: Обработка ошибок при проверке роли магазина
        except sqlite3.Error as error:
            print(
                f"❌ Ошибка SQLite при проверке роли магазина: "
                f"{type(error).__name__}: {error}"
            )

            msg = (
                f"{self.dn_em} ᴨᴩоизоɯᴧᴀ оɯибᴋᴀ ᴨᴩи ᴩᴀбоᴛᴇ ᴄ бᴀзой дᴀнных."
                f"\n\n-# {self.ow_em} ᴄоздᴀᴛᴇᴧь боᴛᴀ оᴄʙᴇдоʍᴧᴇн об ϶ᴛоʍ."
            )

            await self.send_message(
                interaction,
                msg,
                True
            )

        except Exception as error:
            print(
                f"❌ Неожиданная ошибка при проверке роли магазина: "
                f"{type(error).__name__}: {error}"
            )

            msg = (
                f"{self.dn_em} ᴨᴩи ᴨᴩᴏʙᴇᴩᴋᴇ ᴩоᴧи ᴨᴩоизоɯᴧᴀ оɯибᴋᴀ."
                f"\n\n-# {self.ow_em} ᴄоздᴀᴛᴇᴧь боᴛᴀ оᴄʙᴇдоʍᴧᴇн об ϶ᴛоʍ."
            )

            await self.send_message(
                interaction,
                msg,
                True
            )
            return

        # LOGIC: Подтверждение добавления роли в магазин
        async def confirm_action(confirm_interaction: discord.Interaction):
            # LOGIC: Добавляем роль в магазин
            await self.manager.add_shop_role(
                role.id,
                price
            )

            # LOGIC: Подготавливаем канал и сообщения: пользователю и в логи
            try:
                l_msg = (
                    f"### {self.sp_em} добᴀʙᴧᴇниᴇ ᴛоʙᴀᴩᴀ\n"
                    f"{self.at_em} ᴨоᴧьзоʙᴀᴛᴇᴧь {confirm_interaction.user.mention} добᴀʙиᴧ ᴩоᴧь ʙ ᴧᴀᴩᴇᴋ.\n"
                    f"{self.at_em} добᴀʙᴧᴇннᴀя ᴩоᴧь: {role.mention}\n"
                    f"{self.at_em} ᴄᴛоиʍоᴄᴛь ᴩоᴧи: `{price}` {self.vl_em}"
                    f"\n\n-# {self.ow_em} ʙ ᴄᴧучᴀᴇ зᴧоуᴨоᴛᴩᴇбᴧᴇния — ʙы ʙ ᴨᴩᴀʙᴇ нᴀᴋᴀзᴀᴛь ᴇᴦо."
                )
            except Exception as e:
                print(f"❌ Ошибка создания l_msg: {type(e).__name__}: {e}")
                return

            # LOGIC: Проверка на канал
            channel = self.bot.get_channel(BotConfig.LOG_CHANNEL)
            if channel is not None:
                await self.send_message(channel, l_msg)
            else:
                print(
                    f"❌ Не удалось отправить лог о добавлении роли в магазин: "
                    f"Канал с ID {BotConfig.LOG_CHANNEL} не найден."
                )

            # LOGIC: Сообщение пользователю о добавлении роли в магазин
            msg = (
                f"{self.gr_em} ᴩоᴧь {role.mention} добᴀʙᴧᴇнᴀ ʙ ʍᴀᴦᴀзин.\n"
                f"{self.gr_em} ᴄᴛоиʍоᴄᴛь ᴩоᴧи: `{price}` {self.vl_em}.\n"
                f"{self.gr_em} ʙ ᴄᴧучᴀᴇ зᴧоуᴨоᴛᴩᴇбᴧᴇния — ʙы будᴇᴛᴇ нᴀᴋᴀзᴀны."
                f"\n\n-# {self.ow_em} ʙозниᴋᴧи ʙоᴨᴩоᴄы, ᴨиɯиᴛᴇ ᴄоздᴀᴛᴇᴧю."
            )
            await self.send_message(
                confirm_interaction,
                msg,
                True
            )

        # LOGIC: Отправка проверки
        view = ConfirmComponent(
            on_confirm=confirm_action,
            is_admin=True
        )

        await interaction.response.send_message(
            view=view,
            ephemeral=True
        )

        view.message = await interaction.original_response()

    # COMMAND: Удаление товара из магазина
    @app_commands.command(name="удалить_товар", description="Удалить роль из магазина.")
    @app_commands.describe(role="Роль, которую нужно удалить из магазина.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_item_command(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
    ):
        # LOGIC: Всевозможные проверки
        try:
            result = await self.manager.shop_role_exists(role.id)
            if not isinstance(result, bool):
                print(
                    f"❌ shop_role_exists() вернул неожиданный результат: "
                    f"{result!r}"
                )

                msg = (
                    f"{self.dn_em} ᴨᴩоизоɯᴧᴀ оɯибᴋᴀ ᴨᴩи ᴨᴩᴏʙᴇᴩᴋᴇ ᴩоᴧи."
                    f"\n\n-# {self.ow_em} ᴄоздᴀᴛᴇᴧь боᴛᴀ оᴄʙᴇдоʍᴧᴇн об ϶ᴛоʍ."
                )

                await self.send_message(
                    interaction,
                    msg,
                    True
                )
                return

            if not result:
                msg = (
                    f"{self.dn_em} ᴩоᴧь {role.mention} нᴇ нᴀйдᴇнᴀ ʙ ʍᴀᴦᴀзинᴇ.\n"
                    f"{self.dn_em} ᴨᴩоʙᴇᴩьᴛᴇ ᴇщё ᴩᴀз ʙыбᴩᴀнную ᴩоᴧь."
                    f"\n\n-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴨиɯиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )
                await self.send_message(
                    interaction,
                    msg,
                    True
                )
                return

        # LOGIC: Обработка ошибок при проверке роли магазина
        except sqlite3.Error as error:
            print(
                f"❌ SQLite ошибка при проверке роли магазина: "
                f"{type(error).__name__}: {error}"
            )

            msg = (
                f"{self.dn_em} ᴨᴩоизоɯᴧᴀ оɯибᴋᴀ ᴨᴩи ᴩᴀбоᴛᴇ ᴄ бᴀзой дᴀнных."
                f"\n\n-# {self.ow_em} ᴄоздᴀᴛᴇᴧь боᴛᴀ оᴄʙᴇдоʍᴧᴇн об ϶ᴛоʍ."
            )

            await self.send_message(
                interaction,
                msg,
                True
            )
            return
        
        except Exception as error:
            print(
                f"❌ Неожиданная ошибка при проверке роли магазина: "
                f"{type(error).__name__}: {error}"
            )

            msg = (
                f"{self.dn_em} ᴨᴩи ᴨᴩᴏʙᴇᴩᴋᴇ ᴩоᴧи ᴨᴩоизоɯᴧᴀ оɯибᴋᴀ."
                f"\n\n-# {self.ow_em} ᴄоздᴀᴛᴇᴧь боᴛᴀ оᴄʙᴇдоʍᴧᴇн об ϶ᴛоʍ."
            )

            await self.send_message(
                interaction,
                msg,
                True
            )
            return

        # LOGIC: Подтверждение удаления роли из магазина
        async def confirm_action(confirm_interaction: discord.Interaction):
            try:
                # LOGIC: Проверяем, что подтверждение нажал тот же администратор
                if confirm_interaction.user.id != interaction.user.id:
                    msg = (
                        f"{self.dn_em} ϶ᴛо ᴨодᴛʙᴇᴩждᴇниᴇ ᴨᴩᴇднᴀзнᴀчᴇно нᴇ дᴧя ʙᴀᴄ."
                        f"\n\n-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴨиɯиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                    )
                    await self.send_message(
                        confirm_interaction,
                        msg,
                        True
                    )
                    return

                # LOGIC: Повторно проверяем роль перед удалением.
                exists = await self.manager.shop_role_exists(role.id)
                if not exists:
                    msg = (
                        f"{self.dn_em} ᴩоᴧь {role.mention} ужᴇ нᴇ нᴀходиᴛᴄя ʙ ʍᴀᴦᴀзинᴇ.\n"
                        f"{self.dn_em} ʙозʍожнᴏ, её ужᴇ удᴀᴧиᴧи дᴩуᴦиᴇ."
                        f"\n\n-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴨиɯиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                    )
                    await self.send_message(
                        confirm_interaction,
                        msg,
                        True
                    )
                    return

                # LOGIC: Удаляем роль
                removed = await self.manager.remove_shop_role(role.id)
                if not isinstance(removed, bool):
                    print(
                        f"❌ remove_shop_role() вернул неожиданный результат: "
                        f"{removed!r}"
                    )

                    msg = (
                        f"{self.dn_em} ᴨᴩоизоɯᴧᴀ оɯибᴋᴀ ᴨᴩи удᴀᴧᴇнии ᴩоᴧи."
                        f"\n\n-# {self.ow_em} ᴄоздᴀᴛᴇᴧь боᴛᴀ оᴄʙᴇдоʍᴧᴇн об ϶ᴛоʍ."
                    )

                    await self.send_message(
                        confirm_interaction,
                        msg,
                        True
                    )
                    return

                if not removed:
                    msg = (
                        f"{self.dn_em} ᴩоᴧь {role.mention} ужᴇ нᴇ нᴀходиᴛᴄя ʙ ʍᴀᴦᴀзинᴇ."
                        f"\n\n-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴨиɯиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                    )
                    await self.send_message(
                        confirm_interaction,
                        msg,
                        True
                    )
                    return

                # LOGIC: Ищем канал логов
                channel = self.bot.get_channel(BotConfig.LOG_CHANNEL)
                if channel is None:
                    print(
                        f"❌ Не удалось найти канал логов. "
                        f"ID: {BotConfig.LOG_CHANNEL}"
                    )
                elif not hasattr(channel, "send"):
                    print(
                        f"❌ Канал логов не поддерживает отправку сообщений: "
                        f"{type(channel).__name__}"
                    )
                else:
                    l_msg = (
                        f"### {self.sp_em} удᴀᴧᴇниᴇ ᴛоʙᴀᴩᴀ\n"
                        f"{self.at_em} ᴨоᴧьзоʙᴀᴛᴇᴧь {confirm_interaction.user.mention} "
                        f"удᴀᴧил ᴩоᴧь ʙ ᴧᴀᴩᴇᴋᴇ.\n"
                        f"{self.at_em} удᴀᴧяᴇʍᴀя ᴩоᴧь: {role.mention}"
                        f"\n\n-# {self.ow_em} ʙ ᴄᴧучᴀᴇ зᴧоуᴨоᴛᴩᴇбᴧᴇния — "
                        f"ʙы ʙ ᴨᴩᴀʙᴇ нᴀᴋᴀзᴀᴛь ᴇᴦо."
                    )

                    # LOGIC: Отправляем сообщение в канал логов
                    try:
                        await self.send_message(
                            channel,
                            l_msg
                        )

                    except discord.Forbidden:
                        print(
                            f"❌ У бота нет прав на отправку логов. "
                            f"Канал: {BotConfig.LOG_CHANNEL}"
                        )

                    except Exception as error:
                        print(
                            f"❌ Неожиданная ошибка при отправке лога: "
                            f"{type(error).__name__}: {error}"
                        )

                # LOGIC: Сообщение пользователю
                msg = (
                    f"{self.gr_em} ᴩоᴧь {role.mention} удᴀᴧᴇнᴀ из ʍᴀᴦᴀзинᴀ.\n"
                    f"{self.gr_em} ʙ ᴄᴧучᴀᴇ зᴧоуᴨоᴛᴩᴇбᴧᴇния — ʙы будᴇᴛᴇ нᴀᴋᴀзᴀны."
                    f"\n\n-# {self.ow_em} ʙозниᴋᴧи ʙоᴨᴩоᴄы, ᴨиɯиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )
                await self.send_message(
                    confirm_interaction,
                    msg,
                    True
                )

            # LOGIC: Обработка ошибок при удалении роли из магазина
            except sqlite3.Error as error:
                print(
                    f"❌ SQLite ошибка при удалении роли из магазина: "
                    f"{type(error).__name__}: {error}"
                )

                e_msg = (
                    f"{self.dn_em} ᴨᴩоизоɯᴧᴀ оɯибᴋᴀ ᴨᴩи ᴩᴀбоᴛᴇ ᴄ бᴀзой дᴀнных."
                    f"\n\n-# {self.ow_em} ᴄоздᴀᴛᴇᴧь боᴛᴀ оᴄʙᴇдоʍᴧᴇн об ϶ᴛоʍ."
                )

                await self.send_message(
                    confirm_interaction,
                    e_msg,
                    True
                )

            except Exception as error:
                print(
                    f"❌ Неожиданная ошибка при удалении роли: "
                    f"{type(error).__name__}: {error}"
                )

                e_msg = (
                    f"{self.dn_em} ᴨᴩи удᴀᴧᴇнии ᴩоᴧи ᴨᴩоизоɯᴧᴀ оɯибᴋᴀ."
                    f"\n\n-# {self.ow_em} ᴄоздᴀᴛᴇᴧь боᴛᴀ оᴄʙᴇдоʍᴧᴇн об ϶ᴛоʍ."
                )

                await self.send_message(
                    confirm_interaction,
                    e_msg,
                    True
                )

        # LOGIC: Отправка подтверждения
        view = ConfirmComponent(
            on_confirm=confirm_action,
            is_admin=True
        )

        await interaction.response.send_message(
            view=view,
            ephemeral=True
        )

        view.message = await interaction.original_response()

# LOGIC: Запуск кога
async def setup(bot):
    await bot.add_cog(ShopCog(bot))