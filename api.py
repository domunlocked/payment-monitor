"""Read-only authenticated API for the local payment dashboard."""

import hmac
from collections.abc import Callable
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response

from database import PaymentDatabase
from khmer_numbers import announcement_text


def _dashboard_payment(payment: dict[str, Any]) -> dict[str, Any]:
    return {
        **payment,
        "announcement": announcement_text(payment["amount"], payment["currency"]),
    }


def create_app(
    database: PaymentDatabase,
    api_token: str,
    cors_origins: tuple[str, ...] = (),
    telegram_connected: Callable[[], bool] = lambda: False,
    static_dir: Path | None = None,
) -> FastAPI:
    """Create the private payment API; every data endpoint requires a bearer token."""
    if len(api_token) < 32 or not api_token.isascii():
        raise ValueError("The API bearer token must contain at least 32 ASCII characters.")
    app = FastAPI(
        title="DomZzz-Payment Speaker local API",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(cors_origins),
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["Authorization"],
        max_age=300,
    )

    @app.middleware("http")
    async def private_response_headers(request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    if static_dir is not None:
        def static_handler(path: Path) -> Callable[[], Any]:
            async def serve() -> FileResponse:
                return FileResponse(path)
            return serve

        for filename, route in (
            ("index.html", "/"),
            ("styles.css", "/styles.css"),
            ("app.js", "/app.js"),
        ):
            file_path = static_dir / filename

            app.add_api_route(
                route, static_handler(file_path), methods=["GET"], include_in_schema=False
            )

    @app.get("/healthz")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    async def authorize(request: Request) -> None:
        header = request.headers.get("authorization", "")
        scheme, separator, supplied = header.partition(" ")
        if (
            not separator
            or scheme.lower() != "bearer"
            or not supplied.isascii()
            or not hmac.compare_digest(supplied.strip(), api_token)
        ):
            raise HTTPException(status_code=401, detail="A valid bearer token is required.")

    @app.get("/api/status")
    async def status(request: Request) -> dict[str, Any]:
        await authorize(request)
        return {"telegram_connected": telegram_connected()}

    @app.get("/api/payments")
    async def payments(
        request: Request,
        after_id: int | None = Query(default=None, ge=0),
        limit: int = Query(default=100, ge=1, le=100),
    ) -> dict[str, Any]:
        await authorize(request)
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
        await authorize(request)
        return Response(
            content=database.export_csv(),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": 'attachment; filename="payment-history.csv"'},
        )

    return app
