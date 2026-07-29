"""
Registers all Telegram command/message/callback handlers on the
python-telegram-bot Application instance.
"""

from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from app.handlers.about import about_command
from app.handlers.help import help_command
from app.handlers.language import language_command, language_select_callback
from app.handlers.settings import settings_command, settings_update_callback
from app.handlers.start import start_command
from app.handlers.tts import plain_text_message, tts_command
from app.handlers.voices import voices_command, voices_select_callback


def register_handlers(application: Application) -> None:
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("tts", tts_command))
    application.add_handler(CommandHandler("voices", voices_command))
    application.add_handler(CommandHandler("language", language_command))
    application.add_handler(CommandHandler("settings", settings_command))

    application.add_handler(CallbackQueryHandler(voices_select_callback, pattern=r"^voices:set:"))
    application.add_handler(CallbackQueryHandler(language_select_callback, pattern=r"^lang:set:"))
    application.add_handler(
        CallbackQueryHandler(settings_update_callback, pattern=r"^settings:(speed|format):")
    )

    # Plain-text messages that aren't commands: convert directly to speech
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, plain_text_message))
