import asyncio
from unittest.mock import AsyncMock

import pytest

from platzi import m3u8
from platzi.m3u8 import _extract_variants, _playlist_uri_lines, _select_variant


def test_extract_variants_resolves_relative_paths() -> None:
    content = """#EXTM3U
#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=1280x720
720/index.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=1400000,RESOLUTION=1920x1080
https://cdn.example.test/1080/index.m3u8
"""

    variants = _extract_variants(content, "https://cdn.example.test/course/master.m3u8")
    assert [variant.url for variant in variants] == [
        "https://cdn.example.test/course/720/index.m3u8",
        "https://cdn.example.test/1080/index.m3u8",
    ]


def test_extract_variants_ignores_non_variant_uris() -> None:
    content = """#EXTM3U
#EXT-X-MEDIA:TYPE=AUDIO,URI="audio/index.m3u8"
#EXT-X-STREAM-INF:BANDWIDTH=800000
video/index.m3u8
"""

    variants = _extract_variants(content, "https://cdn.example.test/course/master.m3u8")
    assert [variant.url for variant in variants] == [
        "https://cdn.example.test/course/video/index.m3u8"
    ]


@pytest.mark.parametrize(
    ("requested", "expected"), [(1080, "hd"), (720, "sd"), (480, "low")]
)
def test_select_variant_uses_resolution_instead_of_order(
    requested: int, expected: str
) -> None:
    content = """#EXTM3U
#EXT-X-STREAM-INF:BANDWIDTH=1400000,RESOLUTION=1920x1080
hd.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=400000,RESOLUTION=640x360
low.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=1280x720
sd.m3u8
"""
    variants = _extract_variants(content, "https://cdn.example.test/master.m3u8")
    assert (
        _select_variant(variants, requested).url
        == f"https://cdn.example.test/{expected}.m3u8"
    )


def test_playlist_uri_lines_resolves_segments() -> None:
    content = """#EXTM3U
#EXTINF:4.0,
segment-001.ts
#EXTINF:4.0,
/media/segment-002.ts
"""

    assert _playlist_uri_lines(
        content, "https://cdn.example.test/course/720/index.m3u8"
    ) == [
        "https://cdn.example.test/course/720/segment-001.ts",
        "https://cdn.example.test/media/segment-002.ts",
    ]


@pytest.mark.parametrize("playlist_height", [360, 720, 1080])
def test_1080_request_downloads_available_quality(
    monkeypatch, tmp_path, playlist_height
) -> None:
    response = AsyncMock()
    response.ok = True
    response.text.return_value = (
        f"#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=1920x{playlist_height}\n"
        "video.m3u8\n"
    )
    client = AsyncMock()
    client.get.return_value = response
    monkeypatch.setattr(m3u8.rnet, "Client", lambda **kwargs: client)
    monkeypatch.setattr(m3u8.shutil, "which", lambda command: command)
    monkeypatch.setattr(m3u8, "_video_height", lambda path: playlist_height)

    async def write_download(url, path, **kwargs):
        path.write_bytes(b"downloaded")

    download = AsyncMock(side_effect=write_download)
    monkeypatch.setattr(m3u8, "_m3u8_dl", download)
    path = tmp_path / "lesson.mp4"
    path.write_bytes(b"existing")

    asyncio.run(
        m3u8.m3u8_dl(
            "https://cdn.example.test/master.m3u8", path, quality="1080", overwrite=True
        )
    )

    assert download.await_count == 1
    assert path.read_bytes() == b"downloaded"
