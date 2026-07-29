"""
/tts command handler, plus a plain-text handler so users can just send
text directly without the /tts prefix.
"""

import asyncio

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from app.audio import cleanup_dir, synthesize_speech
from app.config import settings
from app.database import get_db_context
from app.handlers._common import get_or_create_user
from app.logger import get_logger
from app.models import UserSettings
from app.tts.factory import get_tts_engine

logger = get_logger(__name__)


async def _generate_and_send(update: Update, text: str) -> None:
    text = text.strip()
    if not text:
        await update.message.reply_text("Send me some text to convert to speech.")
        return
    if len(text) > settings.MAX_TEXT_LENGTH:
        await update.message.reply_text(
            f"That's too long ({len(text)} characters). Please keep it under "
            f"{settings.MAX_TEXT_LENGTH} characters."
        )
        return

    tg_user = update.effective_user
    with get_db_context() as db:
        user = get_or_create_user(db, tg_user)
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
        voice_id = user_settings.voice_id
        language_code = user_settings.language_code
        speed = user_settings.speed
        audio_format = user_settings.audio_format

    await update.effective_chat.send_action(ChatAction.RECORD_VOICE)
    status_message = await update.message.reply_text("🎙️ Generating audio...")

    tmp_dir = None
    try:
        engine = get_tts_engine()
        # synthesize_speech is blocking (network + subprocess calls) —
        # run it off the event loop so other users' requests aren't blocked.
        final_path, tmp_dir = await asyncio.to_thread(
            synthesize_speech, engine, text, voice_id, language_code, speed, audio_format
        )

        await update.effective_chat.send_action(ChatAction.UPLOAD_VOICE)
        with open(final_path, "rb") as audio_file:
            if audio_format == "ogg":
                await update.message.reply_voice(voice=audio_file)
            else:
                await update.message.reply_audio(audio=audio_file, title="Text to Speech")

        await status_message.delete()
        logger.info("TTS sent: telegram_id=%d chars=%d format=%s", tg_user.id, len(text), audio_format)

    except Exception:
        logger.exception("TTS generation failed for telegram_id=%d", tg_user.id)
        await status_message.edit_text(
            "⚠️ Something went wrong generating that audio. Please try again."
        )
    finally:
        if tmp_dir:
            cleanup_dir(tmp_dir)


async def tts_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = " ".join(context.args) if context.args else None

    if not text and update.message.reply_to_message and update.message.reply_to_message.text:
        text = update.message.reply_to_message.text

    if not text:
        await update.message.reply_text(
            "Usage: `/tts <text>` — or reply to a text message with /tts.",
            parse_mode="Markdown",
        )
        return

    await _generate_and_send(update, text)


async def plain_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles plain-text messages that aren't commands — converts them directly."""
    text = update.message.text or ""
    await _generate_and_send(update, text)
