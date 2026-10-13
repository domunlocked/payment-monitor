"""Loopback API with narrowly scoped access through an optional HTTPS tunnel."""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
import hashlib
import hmac
from pathlib import Path
import secrets
from typing import Any, AsyncIterator
from urllib.parse import urlsplit

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse, Response

from database import PaymentDatabase
from khmer_numbers import announcement_text

_SESSION_COOKIE = "payment_monitor_session"
_SESSION_MAX_AGE = 12 * 60 * 60
_REMOTE_DASHBOARD_ORIGIN = "https://domunlocked.github.io"
_REMOTE_READ_PATHS = frozenset({"/api/status", "/api/latest-payment", "/api/payments"})


def _dashboard_payment(payment: dict[str, Any]) -> dict[str, Any]:
    return {
        **payment,
        "announcement": announcement_text(payment["amount"], payment["currency"]),
    }


def _issue_session(api_token: str) -> str:
    issued_at = str(int(datetime.now(timezone.utc).timestamp()))
    payload = f"{issued_at}.{secrets.token_urlsafe(32)}"
    signature = hmac.new(
        api_token.encode("ascii"), payload.encode("ascii"), hashlib.sha256
    ).hexdigest()
    return f"{payload}.{signature}"


def _valid_session(value: str | None, api_token: str) -> bool:
    if not value:
        return False
    parts = value.split(".")
    if len(parts) != 3:
        return False
    issued_at, nonce, signature = parts
    if not nonce:
        return False
    try:
        timestamp = int(issued_at)
    except ValueError:
        return False
    now = int(datetime.now(timezone.utc).timestamp())
    if timestamp > now + 60 or now - timestamp > _SESSION_MAX_AGE:
        return False
    payload = f"{issued_at}.{nonce}"
    expected = hmac.new(
        api_token.encode("ascii"), payload.encode("ascii"), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)


def create_app(
    database: PaymentDatabase,
    api_token: str,
    listener: Any | None = None,
    static_dir: Path | None = None,
    api_origin: str = "http://127.0.0.1:8765",
    remote_api_origin: str | None = None,
    remote_access_token: str | None = None,
    auto_start_listener: bool = False,
    background_worker: Any | None = None,
) -> FastAPI:
    """Create the local app with cookie-protected local routes and remote read-only access."""
    if len(api_token) < 32 or not api_token.isascii():
        raise ValueError("The private API token must contain at least 32 ASCII characters.")
    parsed_origin = urlsplit(api_origin)
    if (
        parsed_origin.scheme != "http"
        or parsed_origin.hostname != "127.0.0.1"
        or not parsed_origin.port
        or parsed_origin.username
        or parsed_origin.password
        or parsed_origin.path
        or parsed_origin.query
        or parsed_origin.fragment
    ):
        raise ValueError("The local dashboard origin must use 127.0.0.1 and an explicit port.")
    expected_host = parsed_origin.netloc.lower()
    if bool(remote_api_origin) != bool(remote_access_token):
        raise ValueError("Remote API origin and access key must be configured together.")
    if remote_access_token and (
        len(remote_access_token) < 32
        or not remote_access_token.isascii()
        or not all(
            character.isalnum() or character in "-_"
            for character in remote_access_token
        )
    ):
        raise ValueError("The remote access key must be at least 32 URL-safe ASCII characters.")
    remote_host = None
    if remote_api_origin:
        parsed_remote_origin = urlsplit(remote_api_origin)
        if (
            parsed_remote_origin.scheme != "https"
            or parsed_remote_origin.hostname is None
            or parsed_remote_origin.username
            or parsed_remote_origin.password
            or parsed_remote_origin.path
            or parsed_remote_origin.query
            or parsed_remote_origin.fragment
        ):
            raise ValueError("The remote API origin must be an HTTPS origin.")
        remote_hostname = parsed_remote_origin.hostname.lower()
        if ":" in remote_hostname:
            remote_hostname = f"[{remote_hostname}]"
        remote_port = parsed_remote_origin.port
        remote_host = remote_hostname + (
            f":{remote_port}" if remote_port not in {None, 443} else ""
        )

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        if background_worker is not None:
            await background_worker.start()
        if auto_start_listener and listener is not None:
            try:
                await listener.start()
            except ValueError as exc:
                import logging

                logging.getLogger("payment-monitor").warning(
                    "Automatic Telegram start skipped: %s", exc
                )
        try:
            yield
        finally:
            if listener is not None:
                await listener.stop()
            if background_worker is not None:
                await background_worker.stop()

    app = FastAPI(
        title="Payment Monitor local API",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )

    @app.middleware("http")
    async def local_security_headers(request: Request, call_next: Any) -> Response:
        request_host = request.headers.get("host", "").lower()
        is_remote = remote_host is not None and request_host == remote_host
        if request_host != expected_host and not is_remote:
            return JSONResponse(
                status_code=421,
                content={"detail": "Use the local dashboard address shown by the app."},
            )
        if is_remote:
            if (
                request.url.path not in _REMOTE_READ_PATHS
                or request.headers.get("origin") != _REMOTE_DASHBOARD_ORIGIN
            ):
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Remote access is restricted to the private dashboard."},
                )
            if request.method == "OPTIONS":
                requested_method = request.headers.get(
                    "access-control-request-method", ""
                ).upper()
                requested_headers = {
                    header.strip().lower()
                    for header in request.headers.get(
                        "access-control-request-headers", ""
                    ).split(",")
                    if header.strip()
                }
                if requested_method != "GET" or not requested_headers.issubset(
                    {"authorization"}
                ):
                    return JSONResponse(status_code=403, content={"detail": "Preflight denied."})
                response = Response(status_code=204)
            elif request.method != "GET":
                return JSONResponse(
                    status_code=405, content={"detail": "Remote access is read-only."}
                )
            else:
                response = await call_next(request)
            response.headers["Access-Control-Allow-Origin"] = _REMOTE_DASHBOARD_ORIGIN
            response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Authorization"
            response.headers["Vary"] = "Origin"
        else:
            response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; connect-src 'self' https:; object-src 'none'; "
            "base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
        )
        return response

    def authorize(request: Request) -> None:
        if remote_host is not None and request.headers.get("host", "").lower() == remote_host:
            supplied = request.headers.get("authorization", "")
            expected = f"Bearer {remote_access_token}"
            if hmac.compare_digest(supplied, expected):
                return
            raise HTTPException(status_code=401, detail="The remote access key is invalid.")
        if not _valid_session(request.cookies.get(_SESSION_COOKIE), api_token):
            raise HTTPException(status_code=401, detail="Reload the local dashboard to start a session.")

    def is_remote_request(request: Request) -> bool:
        return remote_host is not None and request.headers.get("host", "").lower() == remote_host

    def remote_payment(payment: dict[str, Any]) -> dict[str, Any]:
        return {
            key: payment[key]
            for key in (
                "id",
                "currency",
                "amount",
                "payment_status",
                "payment_datetime",
                "transaction_id",
                "received_at",
            )
            if key in payment
        } | {"announcement": announcement_text(payment["amount"], payment["currency"])}

    def authorize_change(request: Request) -> None:
        authorize(request)
        if request.headers.get("origin") != api_origin:
            raise HTTPException(status_code=403, detail="This action is allowed only from the local dashboard.")
        fetch_site = request.headers.get("sec-fetch-site")
        if fetch_site and fetch_site != "same-origin":
            raise HTTPException(status_code=403, detail="Cross-site requests are not allowed.")

    if static_dir is not None:
        index_path = static_dir / "index.html"

        @app.get("/", include_in_schema=False)
        async def dashboard() -> FileResponse:
            response = FileResponse(index_path)
            response.set_cookie(
                _SESSION_COOKIE,
                _issue_session(api_token),
                max_age=_SESSION_MAX_AGE,
                httponly=True,
                secure=False,
                samesite="strict",
                path="/",
            )
            return response

        def static_handler(path: Path) -> Any:
            async def serve() -> FileResponse:
                return FileResponse(path)

            return serve

        for filename in (
            "styles.css",
            "remote-config.js",
            "payment_notifications.js",
            "phone_speech.js",
            "app.js",
        ):
            file_path = static_dir / filename
            app.add_api_route(
                f"/{filename}",
                static_handler(file_path),
                methods=["GET"],
                include_in_schema=False,
            )

    @app.get("/healthz")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "payment-monitor"}

    @app.get("/api/status")
    async def status(request: Request) -> dict[str, Any]:
        authorize(request)
        if listener is None:
            result = {
                "listener_state": "stopped",
                "listener_running": False,
                "telegram_connected": False,
                "message": "The Telegram listener is unavailable.",
            }
        else:
            result = listener.status()
        result["server_time"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        _, rows = database.latest(limit=1)
        result["last_payment_received_at"] = rows[-1]["received_at"] if rows else None
        return result

    @app.post("/api/listener/start")
    async def start_listener(request: Request) -> dict[str, Any]:
        authorize_change(request)
        if listener is None:
            raise HTTPException(status_code=503, detail="The Telegram listener is unavailable.")
        try:
            return await listener.start()
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.post("/api/listener/stop")
    async def stop_listener(request: Request) -> dict[str, Any]:
        authorize_change(request)
        if listener is None:
            raise HTTPException(status_code=503, detail="The Telegram listener is unavailable.")
        return await listener.stop()

    @app.get("/api/latest-payment")
    async def latest_payment(request: Request) -> dict[str, Any]:
        authorize(request)
        _, rows = database.latest(limit=1)
        payment = rows[-1] if rows else None
        if payment and is_remote_request(request):
            payment = remote_payment(payment)
        else:
            payment = _dashboard_payment(payment) if payment else None
        return {"payment": payment}

    @app.get("/api/payments")
    async def payments(
        request: Request,
        after_id: int | None = Query(default=None, ge=0),
        limit: int = Query(default=100, ge=1, le=100),
    ) -> dict[str, Any]:
        authorize(request)
        if after_id is None:
            cursor, rows = database.latest(limit=min(limit, 50))
            return {
                "payments": [
                    remote_payment(row) if is_remote_request(request)
                    else _dashboard_payment(row)
                    for row in rows
                ],
                "cursor": cursor,
                "initial": True,
            }
        rows = database.after(after_id, limit=limit)
        cursor = rows[-1]["id"] if rows else after_id
        return {
            "payments": [
                remote_payment(row) if is_remote_request(request)
                else _dashboard_payment(row)
                for row in rows
            ],
            "cursor": cursor,
            "initial": False,
        }

    @app.get("/api/payments.csv")
    async def payments_csv(request: Request) -> Response:
        authorize(request)
        return Response(
            content=database.export_csv(),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": 'attachment; filename="payment-history.csv"'},
        )

    return app
