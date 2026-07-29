"""
/about command handler.
"""

from telegram import Update
from telegram.ext import ContextTypes

ABOUT_TEXT = (
    "🔊 *Text-to-Speech Bot*\n\n"
    "Converts your text into natural-sounding speech, with multiple "
    "voices, languages, adjustable speed, and audio format options.\n\n"
    "Built with python-telegram-bot, FastAPI, and ffmpeg — hosted on Railway."
)


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(ABOUT_TEXT, parse_mode="Markdown")
