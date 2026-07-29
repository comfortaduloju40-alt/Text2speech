"""
/language command handler — lets users set the TTS language. A curated
set of common languages is shown as buttons; any language code the
active engine supports can be set directly with `/language <code>`.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.database import get_db_context
from app.handlers._common import get_or_create_user
from app.logger import get_logger
from app.models import UserSettings
from app.tts.factory import get_tts_engine

logger = get_logger(__name__)

_COMMON_LANGUAGES = ["en", "es", "fr", "de", "hi", "ar", "pt", "ru", "ja", "zh-CN", "it", "ko"]


def _build_keyboard() -> InlineKeyboardMarkup:
    all_langs = dict(get_tts_engine().list_languages())
    rows, row = [], []
    for code in _COMMON_LANGUAGES:
        if code not in all_langs:
            continue
        row.append(InlineKeyboardButton(all_langs[code], callback_data=f"lang:set:{code}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(rows)


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    all_langs = dict(get_tts_engine().list_languages())

    if context.args:
        code = context.args[0]
        if code not in all_langs:
            await update.message.reply_text(
                f"'{code}' isn't a supported language code for the current TTS engine."
            )
            return
        tg_user = update.effective_user
        with get_db_context() as db:
            user = get_or_create_user(db, tg_user)
            user_settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
            user_settings.language_code = code
        await update.message.reply_text(f"✅ Language set to *{all_langs[code]}*.", parse_mode="Markdown")
        return

    await update.message.reply_text(
        "Choose a language (or use `/language <code>` for any supported code):",
        parse_mode="Markdown",
        reply_markup=_build_keyboard(),
    )


async def language_select_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    code = query.data.split(":")[-1]
    all_langs = dict(get_tts_engine().list_languages())
    if code not in all_langs:
        await query.edit_message_text("That language is no longer available.")
        return

    tg_user = query.from_user
    with get_db_context() as db:
        user = get_or_create_user(db, tg_user)
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
        user_settings.language_code = code

    await query.edit_message_text(f"✅ Language set to *{all_langs[code]}*.", parse_mode="Markdown")
