"""
/voices command handler — lets users pick a voice via inline buttons.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.database import get_db_context
from app.handlers._common import get_or_create_user
from app.logger import get_logger
from app.models import UserSettings
from app.tts.factory import get_tts_engine

logger = get_logger(__name__)


def _build_keyboard() -> InlineKeyboardMarkup:
    voices = get_tts_engine().list_voices()
    rows = [[InlineKeyboardButton(v.label, callback_data=f"voices:set:{v.id}")] for v in voices]
    return InlineKeyboardMarkup(rows)


async def voices_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Choose a voice:", reply_markup=_build_keyboard())


async def voices_select_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    voice_id = query.data.split(":")[-1]
    engine = get_tts_engine()
    voice = next((v for v in engine.list_voices() if v.id == voice_id), None)
    if voice is None:
        await query.edit_message_text("That voice is no longer available.")
        return

    tg_user = query.from_user
    with get_db_context() as db:
        user = get_or_create_user(db, tg_user)
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
        user_settings.voice_id = voice.id
        if voice.language_code != "*":
            user_settings.language_code = voice.language_code

    await query.edit_message_text(f"✅ Voice set to *{voice.label}*.", parse_mode="Markdown")
