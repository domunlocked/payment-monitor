"""Detect actual local Khmer voices and serialize optional local speech jobs."""

import asyncio
import inspect
import locale
from dataclasses import dataclass
from typing import Any, Callable

SAMPLE_SENTENCE = "ទទួលបានប្រាក់ ប្រាំម៉ឺនរៀល"


@dataclass(frozen=True)
class Voice:
    identifier: str
    name: str
    language: str


def _language_codes(raw_languages: Any) -> list[str]:
    languages = []
    if isinstance(raw_languages, (bytes, str)):
        raw_languages = (raw_languages,)
    for language in raw_languages or ():
        if isinstance(language, bytes):
            value = language.decode("ascii", errors="ignore")
            if len(language) >= 2:
                language_id = int.from_bytes(language[:2], "little")
                value = f"{value} {locale.windows_locale.get(language_id, '')}"
            languages.append(value)
        elif isinstance(language, str):
            languages.append(language)
    return languages


def installed_khmer_voices() -> list[Voice]:
    """Return only installed pyttsx3 voices positively identified as Khmer."""
    try:
        import pyttsx3
    except ImportError:
        return []
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    result = []
    for voice in voices:
        languages = _language_codes(getattr(voice, "languages", []))
        language_text = " ".join(languages).lower()
        name = str(getattr(voice, "name", ""))
        if "km" in language_text:
            result.append(
                Voice(
                    identifier=str(voice.id),
                    name=name,
                    language=language_text or "km",
                )
            )
    return result


class SpeechQueue:
    """Run speech callbacks in insertion order, never overlapping announcements."""

    def __init__(self, speak: Callable[[str], Any]) -> None:
        self._speak = speak
        self._queue: asyncio.Queue[str | None] = asyncio.Queue()
        self._worker: asyncio.Task[None] | None = None

    async def start(self) -> None:
        if self._worker is None or self._worker.done():
            self._worker = asyncio.create_task(self._run())

    async def enqueue(self, text: str) -> None:
        if not text.strip():
            raise ValueError("Speech text must not be empty.")
        await self.start()
        await self._queue.put(text)

    async def _run(self) -> None:
        while True:
            text = await self._queue.get()
            try:
                if text is None:
                    return
                result = self._speak(text)
                if inspect.isawaitable(result):
                    await result
            finally:
                self._queue.task_done()

    async def drain(self) -> None:
        await self._queue.join()

    async def close(self) -> None:
        if self._worker is not None and not self._worker.done():
            await self._queue.put(None)
            await self._worker
        self._worker = None


def main() -> int:
    try:
        voices = installed_khmer_voices()
    except Exception as exc:
        print(f"Could not inspect installed voices ({type(exc).__name__}).")
        return 1
    if not voices:
        print(
            "No installed local Khmer voice was detected. No English voice will be "
            "used as a substitute. Install a genuine Khmer system voice, if available "
            "for your device, and check again."
        )
        return 2
    for voice in voices:
        print(f"{voice.name} ({voice.language})")
    print("Voice detection is not a pronunciation-quality test; test the voice on-device.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
