import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from platzi import collectors


@pytest.mark.parametrize("recover", [True, False])
def test_get_unit_retries_failed_pages_and_preserves_cause(monkeypatch, recover):
    async def no_delay(seconds):
        pass

    monkeypatch.setattr(asyncio, "sleep", no_delay)
    pages = []
    for index in range(3):
        page = MagicMock()
        page.goto = AsyncMock()
        page.close = AsyncMock()
        if not recover or index < 2:
            page.goto.side_effect = TimeoutError("navigation timed out")
        page.locator.return_value.first.text_content = AsyncMock(return_value="Lesson")
        page.locator.return_value.first.wait_for = AsyncMock()
        page.locator.return_value.first.is_visible = AsyncMock(return_value=True)
        page.locator.return_value.is_visible = AsyncMock(return_value=False)
        pages.append(page)
    context = MagicMock()
    context.new_page = AsyncMock(side_effect=pages)
    url = "https://example.test/lesson"

    if recover:
        unit = asyncio.run(collectors.get_unit(context, url))
        assert unit.title == "Lesson"
    else:
        with pytest.raises(RuntimeError, match="navigation timed out") as error:
            asyncio.run(collectors.get_unit(context, url))
        assert url in str(error.value)

    assert context.new_page.await_count == 3
    for page in pages:
        page.close.assert_awaited_once()


def test_get_unit_does_not_treat_unloaded_player_as_reading(monkeypatch):
    async def no_delay(seconds):
        pass

    monkeypatch.setattr(asyncio, "sleep", no_delay)
    page = MagicMock()
    page.goto = AsyncMock()
    page.close = AsyncMock()
    page.locator.return_value.first.text_content = AsyncMock(return_value="Lesson")
    page.locator.return_value.first.wait_for = AsyncMock(
        side_effect=TimeoutError("player and reading absent")
    )
    context = MagicMock()
    context.new_page = AsyncMock(return_value=page)

    with pytest.raises(RuntimeError, match="player and reading absent"):
        asyncio.run(collectors.get_unit(context, "https://example.test/lesson"))

    assert page.locator.return_value.first.wait_for.await_count == 3
    page.locator.return_value.first.is_visible.assert_not_called()
