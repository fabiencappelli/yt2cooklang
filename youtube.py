import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs


def extract_video_id(url: str) -> str:
    parsed = urlparse(url)

    if parsed.hostname == "youtu.be":
        return parsed.path.lstrip("/")

    if parsed.hostname and "youtube.com" in parsed.hostname:
        query = parse_qs(parsed.query)
        if "v" in query:
            return query["v"][0]

    raise ValueError(f"Impossible d'extraire l'id YouTube depuis : {url}")


def fetch_metadata(url: str) -> dict:
    opts = {
        "quiet": True,
        "skip_download": True,
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)

    return {
        "title": info.get("title"),
        "description": info.get("description"),
        "webpage_url": info.get("webpage_url", url),
        "channel": info.get("channel"),
    }


def fetch_transcript(url: str, languages: list[str] | None = None) -> str:
    video_id = extract_video_id(url)
    languages = languages or ["fr", "en"]

    ytt_api = YouTubeTranscriptApi()
    fetched = ytt_api.fetch(video_id, languages=languages)

    return "\n".join(snippet.text for snippet in fetched)