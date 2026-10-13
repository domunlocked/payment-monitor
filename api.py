"""Same-origin, loopback-only API for the local payment monitor."""

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
    auto_start_listener: bool = False,
) -> FastAPI:
    """Create the local app; a server-signed HttpOnly cookie protects private routes."""
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

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
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

    app = FastAPI(
        title="Payment Monitor local API",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )

    @app.middleware("http")
    async def local_security_headers(request: Request, call_next: Any) -> Response:
        if request.headers.get("host", "").lower() != expected_host:
            return JSONResponse(
                status_code=421,
                content={"detail": "Use the local dashboard address shown by the app."},
            )
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; connect-src 'self'; object-src 'none'; "
            "base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
        )
        return response

    def authorize(request: Request) -> None:
        if not _valid_session(request.cookies.get(_SESSION_COOKIE), api_token):
            raise HTTPException(status_code=401, detail="Reload the local dashboard to start a session.")

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

        for filename in ("styles.css", "app.js"):
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
            return {
                "listener_state": "stopped",
                "listener_running": False,
                "telegram_connected": False,
                "message": "The Telegram listener is unavailable.",
            }
        return listener.status()

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
        return {"payment": _dashboard_payment(payment) if payment else None}

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
                "payments": [_dashboard_payment(row) for row in rows],
                "cursor": cursor,
                "initial": True,
            }
        rows = database.after(after_id, limit=limit)
        cursor = rows[-1]["id"] if rows else after_id
        return {
            "payments": [_dashboard_payment(row) for row in rows],
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
