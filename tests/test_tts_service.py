import asyncio

from tts_service import SpeechQueue


def test_speech_queue_speaks_in_order() -> None:
    async def check_order() -> list[str]:
        spoken = []

        async def speak(text: str) -> None:
            await asyncio.sleep(0)
            spoken.append(text)

        queue = SpeechQueue(speak)
        await queue.enqueue("first")
        await queue.enqueue("second")
        await queue.enqueue("third")
        await queue.drain()
        await queue.close()
        return spoken

    assert asyncio.run(check_order()) == ["first", "second", "third"]
