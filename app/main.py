"""
FastAPI application entrypoint. Runs the bot in webhook mode: Telegram
POSTs updates to /webhook/<secret>, forwarded to python-telegram-bot's
Application. Also serves /health for Railway's health check.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from telegram import Update
from telegram.ext import Application

from app.config import settings
from app.database import init_db
from app.handlers import register_handlers
from app.logger import get_logger

logger = get_logger(__name__)

telegram_app: Application = Application.builder().token(settings.BOT_TOKEN).build()
register_handlers(telegram_app)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    await telegram_app.initialize()
    await telegram_app.bot.set_webhook(url=settings.full_webhook_url, allowed_updates=Update.ALL_TYPES)
    await telegram_app.start()
    logger.info("Bot started. Webhook set to %s", settings.full_webhook_url)

    yield

    await telegram_app.stop()
    await telegram_app.shutdown()
    logger.info("Bot shut down cleanly.")


app = FastAPI(title="Telegram TTS Bot", lifespan=lifespan)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post(settings.webhook_path)
async def telegram_webhook(request: Request) -> Response:
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return Response(status_code=200)
