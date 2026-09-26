import discord
import traceback

from discord import app_commands
from discord.ext import commands

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

# LOGIC: Основной функционал обработки ошибок
class Errors(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # VARIABLE: Эмодзи для сообщений
        self.dn_em = "<a:denied_emoji:1552780290609512658>"
        self.wt_em = "<a:wait_emoji:1552785236549443634>"
        self.ow_em = "<a:owner_emoji:1552781248236097546>"

        # Глобальный обработчик ошибок slash-команд
        self.bot.tree.on_error = self.on_app_command_error

    # METHOD: Форматирование списка элементов
    @staticmethod
    def format_list(items, formatter=str, limit=2):
        visible = items[:limit]

        result = ", ".join(
            formatter(item)
            for item in visible
        )

        remaining = len(items) - len(visible)

        if remaining > 0:
            result += f" и ᴇщё {remaining}"

        return result

    # METHOD: ERROR SEND
    async def send_error(
        self,
        interaction: discord.Interaction,
        content: str
    ):
        try:
            msg = content
            view = DefaultComponent(msg)
            if interaction.response.is_done():
                await interaction.followup.send(
                    view=view,
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    view=view,
                    ephemeral=True
                )

        except Exception as e:
            print(
                f"❌ Не удалось отправить ошибку пользователю: "
                f"{type(e).__name__}: {e}"
            )

    # LOGIC: GLOBAL APP COMMAND ERROR
    async def on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):

        # ! CommandInvokeError
        # LOGIC: Распаковываем ошибку команды
        if isinstance(
            error,
            app_commands.CommandInvokeError
        ):
            error = error.original

        # ! MissingPermissions
        # LOGIC: Отсутствуют необходимые права
        elif isinstance(
            error,
            app_commands.MissingPermissions
        ):
            permissions = self.format_list(
                error.missing_permissions,
                lambda permission: f"`{permission.replace('_', ' ').title()}`"
            )

            await self.send_error(
                interaction,
                (
                    f"{self.dn_em} у ʙᴀᴄ нᴇдоᴄᴛᴀᴛочно ᴨᴩᴀʙ!\n"
                    f"{self.dn_em} нᴇобходиʍы: {permissions}"
                    f"\n\n-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )
            )
            return

        # ! BotMissingPermissions
        # LOGIC: Отсутствуют права бота
        elif isinstance(
            error,
            app_commands.BotMissingPermissions
        ):
            permissions = self.format_list(
                error.missing_permissions,
                lambda permission: f"`{permission.replace('_', ' ').title()}`"
            )

            await self.send_error(
                interaction,
                (
                    f"{self.dn_em} у боᴛᴀ нᴇдоᴄᴛᴀᴛочно ᴨᴩᴀʙ!\n"
                    f"{self.dn_em} нᴇобходиʍы: {permissions}"
                    f"\n\n-# {self.ow_em} ʙозниᴋᴧи ᴄᴧожноᴄᴛи, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )
            )
            return

        # ! MissingRole
        # LOGIC: Отсутствует конкретная роль
        elif isinstance(
            error,
            app_commands.MissingRole
        ):
            await self.send_error(
                interaction,
                (
                    f"{self.dn_em} у ʙᴀᴄ нᴇᴛ нᴇобходиʍой ᴩоᴧи!\n"
                    f"{self.dn_em} ᴛᴩᴇбуᴇᴛᴄя: <@&{error.missing_role}>!"
                    f"\n\n-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )
            )
            return

        # ! MissingAnyRole
        # LOGIC: Отсутствует любая роль
        elif isinstance(
            error,
            app_commands.MissingAnyRole
        ):
            roles = self.format_list(
                error.missing_roles,
                lambda role_id: f"<@&{role_id}>"
            )

            await self.send_error(
                interaction,
                (
                    f"{self.dn_em} у ʙᴀᴄ нᴇᴛ нᴇобходиʍых ᴩоᴧᴇй!\n"
                    f"{self.dn_em} нᴇдоᴄᴛᴀᴛочно: {roles}"
                    f"\n\n-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )
            )
            return

        # ! NoPrivateMessage
        # LOGIC: Проверка, что вызвана на сервере
        elif isinstance(
            error,
            app_commands.NoPrivateMessage
        ):
            await self.send_error(
                interaction,
                f"{self.dn_em} у ʙᴀᴄ нᴇᴛ доᴄᴛуᴨᴀ ᴋ ϶ᴛой ᴋоʍᴀндᴇ ʙ ᴧичных ᴄообщᴇния!\n\n-# {self.ow_em} боᴛ нᴇ ᴨᴩᴇднᴀзнᴀчᴇн дᴧя ᴧичных ᴄообщᴇний."
            )
            return

        # ! CommandOnCooldown
        # LOGIC: Команда находится в кулдауне
        elif isinstance(
            error,
            app_commands.CommandOnCooldown
        ):
            await self.send_error(
                interaction,
                (
                    f"{self.wt_em} ᴋоʍᴀндᴀ нᴀходиᴛᴄя ʙ ᴋуᴧдᴀунᴇ!\n"
                    f"{self.wt_em} ᴨодождиᴛᴇ {error.retry_after:.1f} секунд "
                    f"\n\n-# {self.ow_em} ᴨᴩоᴄᴛиᴛᴇ зᴀ нᴇудобᴄᴛʙᴀ."
                )
            )
            return

        # ! CheckFailure
        # LOGIC: Проверка не пройдена
        elif isinstance(
            error,
            app_commands.CheckFailure
        ):
            await self.send_error(
                interaction,
                f"{self.dn_em} у ʙᴀᴄ нᴇᴛ доᴄᴛуᴨᴀ ᴋ ϶ᴛой ᴋоʍᴀндᴇ!\n\n-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
            )
            return

        # =============================================
        # =============================================
        # =============================================

        # ! TransformerError
        # LOGIC: Ошибка трансформера
        elif isinstance(
            error,
            app_commands.TransformerError
        ):
            await self.send_error(
                interaction,
                (
                    f"{self.dn_em} нᴇʙᴇᴩный ɸоᴩʍᴀᴛ ᴀᴩᴦуʍᴇнᴛᴀ:\n"
                    f"`{error.value}`"
                    f"\n\n-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )
            )
            return

        # ! TranslationError
        # LOGIC: Ошибка при переводе команды
        elif isinstance(error, app_commands.TranslationError):
            await self.send_error(
                interaction,
                (
                    f"{self.dn_em} оɯибᴋᴀ ᴨᴩи ᴨᴇᴩᴇʙодᴇ ᴋоʍᴀнды"
                    f"\n\n-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )
            )
            return

        # =============================================
        # =============================================
        # =============================================

        # ! CommandNotFound
        # LOGIC: Команда не найдена
        elif isinstance(
            error,
            app_commands.CommandNotFound
        ):
            return

        # ! CommandSignatureMismatch
        # LOGIC: Сигнатура команды не совпадает с зарегистрированной версией дискорда
        elif isinstance(
            error,
            app_commands.CommandSignatureMismatch
        ):
            await self.send_error(
                interaction,
                (
                    f"{self.dn_em} ᴄиᴦнᴀᴛуᴩᴀ ᴋоʍᴀнды нᴇ ᴄоʙᴨᴀдᴀᴇᴛ c ʙᴇᴩᴄиᴇй ᴋоʍᴀнд ᴅɪsᴄᴏʀᴅ\n"
                    f"{self.dn_em} ᴨоᴨᴩобуйᴛᴇ ᴄинхᴩонизиᴩоʙᴀᴛь ᴋоʍᴀнды."
                    f"\n\n-# {self.ow_em} ʙозниᴋᴧи ᴄᴧожноᴄᴛи, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )
            )
            return

        # ! CommandAlreadyRegistered
        # LOGIC: Эта команда уже зарегистрирована 
        elif isinstance(
            error,
            app_commands.CommandAlreadyRegistered
        ):
            await self.send_error(
                interaction,
                (
                    f"{self.dn_em} ϶ᴛᴀ ᴋоʍᴀндᴀ ужᴇ зᴀᴩᴇᴦиᴄᴛᴩиᴩоʙᴀнᴀ.\n"
                    f"{self.dn_em} ᴨᴩоʙᴇᴩьᴛᴇ зᴀᴦᴩузᴋу cog и ᴩᴇᴦиᴄᴛᴩᴀцию ᴋоʍᴀнд."
                    f"\n\n-# {self.ow_em} ʙозниᴋᴧи ᴄᴧожноᴄᴛи, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )
            )
            return

        # ! CommandLimitReached
        # LOGIC: Достигнут лимит Discord для application-команд
        elif isinstance(
            error,
            app_commands.CommandLimitReached
        ):
            await self.send_error(
                interaction,
                (
                    f"{self.dn_em} доᴄᴛиᴦнуᴛ ᴧиʍиᴛ ᴅɪsᴄᴏʀᴅ дᴧя ᴀᴘᴘʟɪᴄᴀᴛɪᴏɴ-ᴋоʍᴀнд.\n"
                    f"{self.dn_em} удᴀᴧиᴛᴇ нᴇнужныᴇ ᴋоʍᴀнды иᴧи ᴨᴩоʙᴇᴩьᴛᴇ ᴩᴇᴦиᴄᴛᴩᴀцию."
                    f"\n\n-# {self.ow_em} ʙозниᴋᴧи ᴄᴧожноᴄᴛи, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )
            )
            return

        # ! MissingApplicationID
        # LOGIC: У бота нету Application ID
        elif isinstance(
            error,
            app_commands.MissingApplicationID
        ):
            await self.send_error(
                interaction,
                (
                    f"{self.dn_em} у боᴛᴀ оᴛᴄуᴛᴄᴛʙуᴇᴛ ᴀᴘᴘʟɪᴄᴀᴛɪᴏɴ ɪᴅ.\n"
                    f"{self.dn_em} ᴨоʙᴛоᴩиᴛᴇ оᴨᴇᴩᴀцию ᴨоᴄᴧᴇ ᴨоᴧноᴦо зᴀᴨуᴄᴋᴀ боᴛᴀ."
                    f"\n\n-# {self.ow_em} ʙозниᴋᴧи ᴄᴧожноᴄᴛи, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )
            )
            return

        # ! CommandSyncFailure
        # LOGIC: Не удачное синхронизирование команд
        elif isinstance(
            error,
            app_commands.CommandSyncFailure
        ):
            await self.send_error(
                interaction,
                (
                    f"{self.dn_em} нᴇ удᴀᴧоᴄь ᴄинхᴩонизиᴩоʙᴀᴛь ᴋоʍᴀнды ᴄ ᴅɪsᴄᴏʀᴅ.\n"
                    f"{self.dn_em} ᴨоᴨᴩобуйᴛᴇ ᴨоʙᴛоᴩиᴛь оᴨᴇᴩᴀцию нᴇʍноᴦо ᴨозжᴇ."
                    f"\n\n-# {self.ow_em} ʙозниᴋᴧи ᴄᴧожноᴄᴛи, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )
            )
            return

        # =============================================
        # =============================================
        # =============================================

        # ! NotFound
        # LOGIC: Ресурс не найден
        elif isinstance(
            error,
            discord.NotFound
        ):
            await self.send_error(
                interaction,
                (
                    f"{self.dn_em} учᴀᴄᴛниᴋ/ᴩᴇᴄуᴩᴄ нᴇ нᴀйдᴇн."
                    f"{self.dn_em} может быᴛь зᴀбᴧоᴋиᴩоʙᴀн/удᴀᴧᴇн."
                    f"\n\n-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )
            )
            return

        # ! Forbidden
        # LOGIC: FORBIDDEN
        elif isinstance(error, discord.Forbidden):
            await self.send_error(
                interaction,
                (
                    f"{self.dn_em} у боᴛᴀ нᴇдоᴄᴛᴀᴛочно ᴨᴩᴀʙ!\n"
                    f"{self.dn_em} ᴅɪsᴄᴏʀᴅ зᴀᴨᴩᴇᴛиᴧ ʙыᴨоᴧнᴇниᴇ ϶ᴛоᴦо дᴇйᴄᴛʙия!"
                    f"\n\n-# {self.ow_em} ʙозниᴋᴧи ᴄᴧожноᴄᴛи, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )
            )
            return

        # ! HTTPException
        # LOGIC: HTTP EXCEPTION
        elif isinstance(error, discord.HTTPException):
            if error.status == 429:
                message = (
                    f"{self.wt_em} ᴄᴧиɯᴋоʍ ʍноᴦо зᴀᴨᴩоᴄоʙ.\n"
                    f"{self.wt_em} ᴨоᴨᴩобуйᴛᴇ нᴇʍноᴦо ᴨозжᴇ."
                    f"\n\n-# {self.ow_em} ᴨᴩоᴄᴛиᴛᴇ зᴀ нᴇудобᴄᴛʙᴀ."
                )

            elif error.status == 400:
                message = (
                    f"{self.dn_em} ᴅɪsᴄᴏʀᴅ оᴛᴋᴧониᴧ зᴀᴨᴩоᴄ.\n"
                    f"{self.dn_em} оɯибᴋᴀ: `ʜᴛᴛᴘ {error.status}`"
                    f"\n\n-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )

            elif 500 <= error.status < 600:
                message = (
                    f"{self.wt_em} ᴅɪsᴄᴏʀᴅ ʙᴩᴇʍᴇнно нᴇдоᴄᴛуᴨᴇн.\n"
                    f"{self.wt_em} ᴨоᴨᴩобуйᴛᴇ ᴨоʙᴛоᴩиᴛь дᴇйᴄᴛʙиᴇ ᴨозжᴇ."
                    f"\n\n-# {self.ow_em} ᴨᴩоᴄᴛиᴛᴇ зᴀ нᴇудобᴄᴛʙᴀ."
                )

            else:
                message = (
                    f"{self.dn_em} оɯибᴋᴀ ᴅɪsᴄᴏʀᴅ ᴀᴘɪ:\n"
                    f"{self.dn_em} `ʜᴛᴛᴘ {error.status}`"
                    f"\n\n-# {self.ow_em} ᴄчиᴛᴀᴇᴛᴇ ϶ᴛо оɯибᴋой, ᴄообщиᴛᴇ ᴄоздᴀᴛᴇᴧю."
                )

            await self.send_error(
                interaction,
                message
            )
            return

        # ! НЕИЗВЕСТНАЯ ОШИБКА
        else:
            # LOGIC: Название команды
            command_name = (
                interaction.command.name
                if interaction.command
                else "Неизвестно"
            )

            print(
                "\n"
                "=========================================\n"
                "⚠️ ОШИБКА SLASH-КОМАНДЫ\n"
                f"Команда: /{command_name}\n"
                f"Тип: {type(error).__name__}\n"
                f"Ошибка: {error}\n"
                "========================================="
            )

            traceback.print_exception(
                type(error),
                error,
                error.__traceback__
            )

            await self.send_error(
                interaction,
                (
                    f"{self.dn_em} ᴨᴩоизоɯᴧᴀ нᴇизʙᴇᴄᴛнᴀя оɯибᴋᴀ.\n"
                    f"{self.dn_em} ᴩᴀзᴩᴀбоᴛчиᴋ ужᴇ уʙᴇдоʍᴧён."
                    f"\n\n-# {self.ow_em} ᴨᴩоᴄᴛиᴛᴇ зᴀ нᴇудобᴄᴛʙᴀ."
                )
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Errors(bot))