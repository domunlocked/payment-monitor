"""Watch one Telegram group and serve its private local payment dashboard API."""

import argparse
import asyncio
import logging
import os
from logging.handlers import RotatingFileHandler

import uvicorn
from telethon import TelegramClient, events
from telethon.errors import RPCError

from api import create_app
from config import PROJECT_DIR, Settings, get_settings
from database import PaymentDatabase
from parser import parse_payment_message
from tts_service import installed_khmer_voices
from dotenv import load_dotenv


def configure_logging(settings: Settings) -> None:
    settings.logs_path.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    file_handler = RotatingFileHandler(
        settings.logs_path / "listener.log",
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logging.basicConfig(
        level=getattr(logging, settings.log_level, logging.INFO),
        handlers=[file_handler, console_handler],
    )
    logging.getLogger("uvicorn.access").disabled = True


async def _telegram_loop(
    settings: Settings, database: PaymentDatabase, connected: dict[str, bool]
) -> None:
    log = logging.getLogger("payment-speaker.telegram")
    client = TelegramClient(
        str(settings.session_path),
        settings.api_id,
        settings.api_hash,
        auto_reconnect=True,
        flood_sleep_threshold=60,
    )

    async def handle_message(event: events.NewMessage.Event) -> None:
        payment = parse_payment_message(event.raw_text or "")
        if payment is None:
            return
        if database.add_payment(payment.to_dict()):
            log.info("Recorded a new payment notification.")
        else:
            log.info("Ignored a duplicate transaction notification.")

    client.add_event_handler(
        handle_message,
        events.NewMessage(chats=settings.chat_id, incoming=True),
    )
    delay = 2
    while True:
        try:
            await client.start()
            connected["value"] = True
            log.info("Telegram listener connected to its configured group.")
            delay = 2
            await client.run_until_disconnected()
            if not client.is_connected():
                connected["value"] = False
        except asyncio.CancelledError:
            connected["value"] = False
            if client.is_connected():
                await client.disconnect()
            raise
        except Exception as exc:
            connected["value"] = False
            log.error(
                "Telegram connection failed (%s); retrying in %s seconds.",
                type(exc).__name__,
                delay,
            )
        if client.is_connected():
            await client.disconnect()
        connected["value"] = False
        await asyncio.sleep(delay)
        delay = min(delay * 2, 60)


async def run_listener(settings: Settings) -> None:
    configure_logging(settings)
    log = logging.getLogger("payment-speaker")
    database = PaymentDatabase(settings.database_path, settings.retention_days)
    connection_state = {"value": False}
    app = create_app(
        database,
        settings.api_token,
        settings.cors_origins,
        lambda: connection_state["value"],
        static_dir=PROJECT_DIR,
    )
    server = uvicorn.Server(
        uvicorn.Config(
            app,
            host=settings.api_host,
            port=settings.api_port,
            log_level=settings.log_level.lower(),
            access_log=False,
        )
    )
    log.info("Starting the local API on %s:%s.", settings.api_host, settings.api_port)
    server_task = asyncio.create_task(server.serve())
    telegram_task = asyncio.create_task(
        _telegram_loop(settings, database, connection_state)
    )
    try:
        completed, _ = await asyncio.wait(
            (server_task, telegram_task),
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in completed:
            task.result()
    finally:
        connection_state["value"] = False
        server.should_exit = True
        if not telegram_task.done():
            telegram_task.cancel()
        try:
            await asyncio.wait_for(
                asyncio.gather(server_task, telegram_task, return_exceptions=True),
                timeout=10,
            )
        except asyncio.TimeoutError:
            server_task.cancel()
            telegram_task.cancel()
            await asyncio.gather(server_task, telegram_task, return_exceptions=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-voice",
        action="store_true",
        help="List installed local Khmer voices without starting the listener.",
    )
    parser.add_argument(
        "--list-groups",
        action="store_true",
        help="Authorize Telegram and list group IDs to configure TELEGRAM_CHAT_ID.",
    )
    args = parser.parse_args()
    if args.check_voice:
        try:
            voices = installed_khmer_voices()
        except Exception as exc:
            print(f"Could not inspect installed voices ({type(exc).__name__}).")
            return 1
        if not voices:
            print("No installed local Khmer voice was detected; English fallback is disabled.")
            return 2
        for voice in voices:
            print(f"{voice.name} ({voice.language})")
        return 0
    if args.list_groups:
        load_dotenv(PROJECT_DIR / ".env")
        try:
            api_id = int(os.getenv("TELEGRAM_API_ID", ""))
            api_hash = os.getenv("TELEGRAM_API_HASH", "")
            if api_id <= 0 or len(api_hash) < 20:
                raise ValueError
        except ValueError:
            print("Set TELEGRAM_API_ID and TELEGRAM_API_HASH in .env before listing groups.")
            return 2

        async def show_groups() -> None:
            client = TelegramClient(
                str(PROJECT_DIR / "payment-monitor.session"), api_id, api_hash
            )
            try:
                await client.start()
                async for dialog in client.iter_dialogs():
                    if dialog.is_group or dialog.is_channel:
                        print(f"{dialog.name}  |  {dialog.id}")
            finally:
                await client.disconnect()

        try:
            asyncio.run(show_groups())
        except (RPCError, OSError) as exc:
            print(f"Could not read Telegram groups ({type(exc).__name__}).")
            return 1
        except KeyboardInterrupt:
            print("\nGroup listing stopped.")
        return 0
    try:
        settings = get_settings()
    except ValueError as exc:
        print(f"Configuration error: {exc}")
        return 2
    try:
        asyncio.run(run_listener(settings))
    except KeyboardInterrupt:
        print("\nListener stopped.")
    except OSError as exc:
        logging.getLogger("payment-speaker").error(
            "The local API could not start (%s). Check the port and firewall settings.",
            type(exc).__name__,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
