"""
/start command handler.
"""

from telegram import Update
from telegram.ext import ContextTypes

from app.database import get_db_context
from app.handlers._common import get_or_create_user
from app.logger import get_logger

logger = get_logger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tg_user = update.effective_user
    if tg_user is None:
        return

    with get_db_context() as db:
        get_or_create_user(db, tg_user)
        logger.info("User interaction: telegram_id=%d username=%s", tg_user.id, tg_user.username)

    text = (
        f"👋 Hi {tg_user.first_name or 'there'}!\n\n"
        "I turn text into natural-sounding speech. Just send me any text "
        "and I'll reply with an audio file.\n\n"
        "*Quick start:*\n"
        "• Just paste text to hear it spoken instantly\n"
        "• `/tts <text>` — same thing, explicitly\n"
        "• `/voices` — choose a voice\n"
        "• `/language` — choose a language\n"
        "• `/settings` — adjust speed and audio format\n\n"
        "Type /help for the full command list."
    )
    await update.message.reply_text(text, parse_mode="Markdown")
