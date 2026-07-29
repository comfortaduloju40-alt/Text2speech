"""
/help command handler.
"""

from telegram import Update
from telegram.ext import ContextTypes

HELP_TEXT = (
    "*Available commands:*\n\n"
    "/tts <text> — Convert text to speech (or just paste text with no command)\n"
    "/voices — Choose a voice\n"
    "/language — Choose a language\n"
    "/settings — View and adjust speed & audio format\n"
    "/about — About this bot\n"
    "/help — Show this message\n\n"
    "💡 Tip: reply to any text message with /tts to convert that message."
)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")
