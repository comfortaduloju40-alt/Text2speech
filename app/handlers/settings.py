"""
/settings command handler — shows current settings and lets users
adjust speech speed and audio format via inline buttons.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.database import get_db_context
from app.handlers._common import get_or_create_user
from app.logger import get_logger
from app.models import UserSettings

logger = get_logger(__name__)

_SPEED_OPTIONS = [0.75, 1.0, 1.25, 1.5, 2.0]
_FORMAT_OPTIONS = ["mp3", "ogg", "wav"]


def _build_keyboard(current_speed: float, current_format: str) -> InlineKeyboardMarkup:
    speed_row = [
        InlineKeyboardButton(
            f"{'✅ ' if s == current_speed else ''}{s}x", callback_data=f"settings:speed:{s}"
        )
        for s in _SPEED_OPTIONS
    ]
    format_row = [
        InlineKeyboardButton(
            f"{'✅ ' if f == current_format else ''}{f.upper()}", callback_data=f"settings:format:{f}"
        )
        for f in _FORMAT_OPTIONS
    ]
    return InlineKeyboardMarkup([speed_row, format_row])


def _summary_text(user_settings: UserSettings) -> str:
    return (
        "⚙️ *Your settings*\n\n"
        f"🎤 Voice: `{user_settings.voice_id}`\n"
        f"🌐 Language: `{user_settings.language_code}`\n"
        f"⏩ Speed: `{user_settings.speed}x`\n"
        f"🎵 Format: `{user_settings.audio_format.upper()}`\n\n"
        "Use /voices or /language to change voice/language. "
        "Tap below to change speed or format:"
    )


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tg_user = update.effective_user
    with get_db_context() as db:
        user = get_or_create_user(db, tg_user)
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
        text = _summary_text(user_settings)
        keyboard = _build_keyboard(user_settings.speed, user_settings.audio_format)

    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)


async def settings_update_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    _, field, value = query.data.split(":")
    tg_user = query.from_user

    with get_db_context() as db:
        user = get_or_create_user(db, tg_user)
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()

        if field == "speed":
            user_settings.speed = float(value)
        elif field == "format":
            user_settings.audio_format = value

        db.flush()
        text = _summary_text(user_settings)
        keyboard = _build_keyboard(user_settings.speed, user_settings.audio_format)

    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
