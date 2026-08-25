from platzi.m3u8 import _extract_variant_urls, _playlist_uri_lines


def test_extract_variant_urls_resolves_relative_paths() -> None:
    content = """#EXTM3U
#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=1280x720
720/index.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=1400000,RESOLUTION=1920x1080
https://cdn.example.test/1080/index.m3u8
"""

    assert _extract_variant_urls(
        content, "https://cdn.example.test/course/master.m3u8"
    ) == [
        "https://cdn.example.test/course/720/index.m3u8",
        "https://cdn.example.test/1080/index.m3u8",
    ]


def test_extract_variant_urls_ignores_non_variant_uris() -> None:
    content = """#EXTM3U
#EXT-X-MEDIA:TYPE=AUDIO,URI="audio/index.m3u8"
#EXT-X-STREAM-INF:BANDWIDTH=800000
video/index.m3u8
"""

    assert _extract_variant_urls(
        content, "https://cdn.example.test/course/master.m3u8"
    ) == ["https://cdn.example.test/course/video/index.m3u8"]


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
