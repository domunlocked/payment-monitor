"""Serve the local dashboard and start the configured Telegram listener on demand."""

import argparse
import asyncio
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import sys
import webbrowser
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import uvicorn
from telethon import TelegramClient, events
from telethon.errors import RPCError

from api import create_app
from config import PROJECT_DIR, Settings, get_settings
from database import PaymentDatabase
from parser import parse_payment_message
from tts_service import installed_khmer_voices


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
    logging.getLogger("telethon").setLevel(logging.WARNING)


def control_local_listener(settings: Settings, action: str) -> int:
    """Read or control the existing loopback service without disclosing credentials."""
    if action not in {"status", "start", "stop", "shutdown"}:
        raise ValueError("Unsupported local listener action.")
    from api import _issue_session

    origin = f"http://{settings.api_host}:{settings.api_port}"
    path = (
        "/api/status"
        if action == "status"
        else "/api/shutdown"
        if action == "shutdown"
        else f"/api/listener/{action}"
    )
    headers = {
        "Cookie": f"payment_monitor_session={_issue_session(settings.api_token)}",
    }
    method = "GET"
    if action != "status":
        headers.update(
            {
                "Origin": origin,
                "Sec-Fetch-Site": "same-origin",
                "Content-Type": "application/json",
            }
        )
        method = "POST"
    request = Request(f"{origin}{path}", headers=headers, method=method)
    try:
        with urlopen(request, timeout=5) as response:
            result = json.load(response)
    except HTTPError as exc:
        try:
            result = json.loads(exc.read().decode("utf-8"))
            message = result.get("detail", f"Local API returned HTTP {exc.code}.")
        except (UnicodeDecodeError, json.JSONDecodeError):
            message = f"Local API returned HTTP {exc.code}."
        print(f"Listener {action} failed: {message}")
        return 1
    except (URLError, TimeoutError, OSError) as exc:
        print(
            "Payment Monitor is not responding at "
            f"{origin} ({type(exc).__name__}). Start it with start_payment_monitor.bat "
            "or run setup_startup.bat."
        )
        return 1

    state = result.get("listener_state", "unknown")
    running = result.get("listener_running") is True
    connected = result.get("telegram_connected") is True
    if action == "status":
        print(f"Listener process: {'running' if running else 'not running'}")
        print(f"Telegram connection: {'connected' if connected else 'disconnected'}")
        print(f"State: {state}")
    elif action == "start":
        print(f"Listener start requested. State: {state}.")
    elif action == "shutdown":
        print("Local dashboard and Telegram listener are shutting down.")
    else:
        print(f"Listener stopped. State: {state}.")
    if result.get("message"):
        print(result["message"])
    return 0


def log_configuration_error(message: str) -> None:
    """Record safe configuration diagnostics before normal file logging is set up."""
    log_path = PROJECT_DIR / "logs" / "startup.log"
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(f"Configuration error: {message}\n")
    except OSError as exc:
        print(f"Could not write startup error log ({type(exc).__name__}).", file=sys.stderr)


class SingleInstanceLock:
    """Hold an OS-managed lock so concurrent launchers cannot run two APIs."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._handle = None

    def acquire(self) -> bool:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self.path.open("a+b")
        self._handle.seek(0, os.SEEK_END)
        if self._handle.tell() == 0:
            self._handle.write(b"\0")
            self._handle.flush()
        self._handle.seek(0)
        try:
            if sys.platform == "win32":
                import msvcrt

                msvcrt.locking(self._handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(self._handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (OSError, BlockingIOError):
            self._handle.close()
            self._handle = None
            return False
        return True

    def release(self) -> None:
        if self._handle is None:
            return
        try:
            self._handle.seek(0)
            if sys.platform == "win32":
                import msvcrt

                msvcrt.locking(self._handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(self._handle.fileno(), fcntl.LOCK_UN)
        finally:
            self._handle.close()
            self._handle = None


class TelegramListenerManager:
    """Own at most one Telegram client task for the lifetime of the local API."""

    def __init__(
        self,
        settings: Settings,
        database: PaymentDatabase,
        client_factory: Callable[..., Any] = TelegramClient,
    ) -> None:
        self.settings = settings
        self.database = database
        self._client_factory = client_factory
        self._task: asyncio.Task[None] | None = None
        self._client: Any | None = None
        self._lock = asyncio.Lock()
        self._state = "stopped"
        self._connected = False
        self._message = "Listener is stopped."

    def _missing_telegram_settings(self) -> list[str]:
        missing = []
        if self.settings.api_id is None:
            missing.append("TELEGRAM_API_ID")
        if not self.settings.api_hash:
            missing.append("TELEGRAM_API_HASH")
        if self.settings.chat_id is None:
            missing.append("TELEGRAM_CHAT_ID")
        return missing

    def status(self) -> dict[str, Any]:
        missing = self._missing_telegram_settings()
        state = self._state
        message = self._message
        if state == "stopped" and missing:
            state = "setup_required"
            message = f"Set {', '.join(missing)} in .env before starting Telegram."
        return {
            "listener_state": state,
            "listener_running": bool(self._task and not self._task.done()),
            "telegram_connected": self._connected,
            "message": message,
        }

    async def start(self) -> dict[str, Any]:
        async with self._lock:
            if self._task is not None and not self._task.done():
                return self.status()
            missing = self._missing_telegram_settings()
            if missing:
                self._state = "setup_required"
                self._connected = False
                self._message = f"Set {', '.join(missing)} in .env before starting Telegram."
                raise ValueError(self._message)
            self._state = "starting"
            self._connected = False
            self._message = "Connecting to the configured Telegram group."
            self._task = asyncio.create_task(self._run())
            return self.status()

    async def stop(self) -> dict[str, Any]:
        async with self._lock:
            task = self._task
            if task is None or task.done():
                self._connected = False
                if self._state != "needs_login":
                    self._state = "stopped"
                    self._message = "Listener is stopped."
                return self.status()
            self._state = "stopping"
            self._message = "Stopping the Telegram listener."
            task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        if self._task is task:
            self._connected = False
            self._state = "stopped"
            self._message = "Listener is stopped."
        return self.status()

    async def _handle_message(self, event: events.NewMessage.Event) -> None:
        payment = parse_payment_message(event.raw_text or "")
        if payment is None:
            return
        chat_id = getattr(event, "chat_id", None) or self.settings.chat_id
        message_id = getattr(event, "id", None)
        inserted = self.database.add_payment(
            payment.to_dict(),
            source_chat_id=chat_id if message_id is not None else None,
            source_message_id=message_id,
        )
        log = logging.getLogger("payment-monitor.telegram")
        if inserted:
            log.info("Recorded a new payment notification.")
        else:
            log.info("Ignored a duplicate transaction notification.")

    async def _run(self) -> None:
        log = logging.getLogger("payment-monitor.telegram")
        delay = 2
        try:
            while True:
                client = None
                try:
                    client = self._client_factory(
                        str(self.settings.session_path),
                        self.settings.api_id,
                        self.settings.api_hash,
                        auto_reconnect=True,
                        flood_sleep_threshold=60,
                    )
                    self._client = client
                    await client.connect()
                    if not await client.is_user_authorized():
                        self._state = "needs_login"
                        self._message = (
                            "Telegram needs a one-time sign-in. In another local "
                            "terminal run: .\\.venv\\Scripts\\python.exe listener.py --login"
                        )
                        log.warning("Telegram session is not authorized; listener was not started.")
                        return

                    last_existing_id = 0
                    pending_messages = []
                    baseline_ready = False

                    async def handle_new_message(event: events.NewMessage.Event) -> None:
                        if not baseline_ready:
                            pending_messages.append(event)
                        elif event.id > last_existing_id:
                            await self._handle_message(event)

                    client.add_event_handler(
                        handle_new_message,
                        events.NewMessage(chats=self.settings.chat_id, incoming=True),
                    )
                    # Install the handler before reading the watermark so updates received
                    # during that request can be buffered and filtered by Telegram message ID.
                    latest_messages = await client.get_messages(
                        self.settings.chat_id, limit=1
                    )
                    last_existing_id = max(
                        (message.id for message in latest_messages), default=0
                    )
                    baseline_ready = True
                    for event in sorted(pending_messages, key=lambda item: item.id):
                        if event.id > last_existing_id:
                            await self._handle_message(event)
                    pending_messages.clear()
                    self._connected = True
                    self._state = "connected"
                    self._message = "Connected to the configured Telegram group."
                    log.info("Telegram listener connected to its configured group.")
                    delay = 2
                    await client.run_until_disconnected()
                    self._connected = False
                    self._state = "reconnecting"
                    self._message = "Telegram disconnected; reconnecting automatically."
                except asyncio.CancelledError:
                    raise
                except Exception as exc:
                    self._connected = False
                    self._state = "reconnecting"
                    self._message = "Telegram connection failed; retrying automatically."
                    log.warning(
                        "Telegram connection failed (%s); retrying in %s seconds.",
                        type(exc).__name__,
                        delay,
                    )
                finally:
                    self._connected = False
                    if client is not None:
                        try:
                            if client.is_connected():
                                await client.disconnect()
                        except Exception as exc:
                            log.warning(
                                "Telegram cleanup failed (%s).", type(exc).__name__
                            )
                    self._client = None
                await asyncio.sleep(delay)
                delay = min(delay * 2, 60)
        except asyncio.CancelledError:
            self._state = "stopped"
            self._connected = False
            self._message = "Listener is stopped."
            raise
        finally:
            self._connected = False
            client = self._client
            self._client = None
            if client is not None:
                try:
                    if client.is_connected():
                        await client.disconnect()
                except Exception as exc:
                    log.warning("Telegram shutdown cleanup failed (%s).", type(exc).__name__)


async def _authorize_telegram(settings: Settings) -> None:
    client = TelegramClient(
        str(settings.session_path), settings.api_id, settings.api_hash
    )
    try:
        await client.start()
        print("Telegram sign-in is saved locally for this Windows account.")
    finally:
        await client.disconnect()


async def _list_groups(settings: Settings) -> None:
    client = TelegramClient(
        str(settings.session_path), settings.api_id, settings.api_hash
    )
    try:
        await client.start()
        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                print(f"{dialog.name}  |  {dialog.id}")
    finally:
        await client.disconnect()


async def run_listener(
    settings: Settings,
    auto_start_listener: bool = False,
    open_dashboard: bool = False,
) -> None:
    configure_logging(settings)
    instance_lock = SingleInstanceLock(settings.logs_path / "service.lock")
    if not instance_lock.acquire():
        logging.getLogger("payment-monitor").info(
            "Payment Monitor is already running; reusing the existing local service."
        )
        return
    try:
        database = PaymentDatabase(settings.database_path, settings.retention_days)
    except Exception:
        instance_lock.release()
        raise
    manager = TelegramListenerManager(settings, database)
    origin = f"http://{settings.api_host}:{settings.api_port}"
    app = create_app(
        database,
        settings.api_token,
        listener=manager,
        static_dir=PROJECT_DIR,
        api_origin=origin,
        remote_api_origin=settings.remote_api_origin,
        remote_access_token=settings.remote_access_token,
        auto_start_listener=auto_start_listener,
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
    app.state.uvicorn_server = server
    logging.getLogger("payment-monitor").info(
        "Starting the local dashboard at %s.", origin
    )
    try:
        server_task = asyncio.create_task(server.serve())
        if open_dashboard:
            while not server.started and not server_task.done():
                await asyncio.sleep(0.1)
            if server.started:
                opened = webbrowser.open(f"{origin}/", new=2)
                if not opened:
                    logging.getLogger("payment-monitor").warning(
                        "Could not open the local dashboard automatically."
                    )
        await server_task
    finally:
        instance_lock.release()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    control = parser.add_mutually_exclusive_group()
    control.add_argument(
        "--status",
        action="store_true",
        help="Show status of the existing local API and Telegram listener.",
    )
    control.add_argument(
        "--start",
        action="store_true",
        help="Start Telegram monitoring through the existing local API.",
    )
    control.add_argument(
        "--stop",
        action="store_true",
        help="Gracefully stop Telegram monitoring without stopping the dashboard.",
    )
    control.add_argument(
        "--shutdown",
        action="store_true",
        help="Gracefully stop Telegram monitoring and the local dashboard service.",
    )
    parser.add_argument(
        "--login",
        action="store_true",
        help="Complete the one-time Telegram user sign-in in this terminal.",
    )
    parser.add_argument(
        "--check-voice",
        action="store_true",
        help="List installed local Khmer voices without starting the listener.",
    )
    parser.add_argument(
        "--list-groups",
        action="store_true",
        help="Sign in and list Telegram group IDs for TELEGRAM_CHAT_ID.",
    )
    parser.add_argument(
        "--autostart",
        action="store_true",
        help="Also start Telegram monitoring when the local API starts.",
    )
    parser.add_argument(
        "--open-dashboard",
        action="store_true",
        help="Open the local dashboard in the default browser after the API starts.",
    )
    args = parser.parse_args()
    if args.open_dashboard and not args.autostart:
        parser.error("--open-dashboard requires --autostart.")
    if (args.autostart or args.open_dashboard) and (
        args.status or args.start or args.stop or args.shutdown
    ):
        parser.error("Startup options cannot be combined with a local control option.")
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

    try:
        settings = get_settings(
            require_telegram=args.login or args.list_groups,
            require_chat=False,
        )
    except ValueError as exc:
        print(f"Configuration error: {exc}")
        log_configuration_error(str(exc))
        return 2

    try:
        if args.login:
            asyncio.run(_authorize_telegram(settings))
        elif args.list_groups:
            asyncio.run(_list_groups(settings))
        elif args.status:
            return control_local_listener(settings, "status")
        elif args.start:
            return control_local_listener(settings, "start")
        elif args.stop:
            return control_local_listener(settings, "stop")
        elif args.shutdown:
            return control_local_listener(settings, "shutdown")
        else:
            asyncio.run(
                run_listener(
                    settings,
                    auto_start_listener=args.autostart,
                    open_dashboard=args.open_dashboard,
                )
            )
    except KeyboardInterrupt:
        print("\nOperation stopped.")
    except (RPCError, OSError) as exc:
        logging.getLogger("payment-monitor").error(
            "Operation failed (%s). Check the local configuration and logs.",
            type(exc).__name__,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
