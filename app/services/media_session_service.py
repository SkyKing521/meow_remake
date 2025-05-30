import asyncio
import logging
from typing import Optional, Dict
import requests
import os

from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MediaSessionService:
    def __init__(self):
        self.last_track = None
        self.last_update = 0
        self.update_interval = 1.0  # seconds

    async def get_current_track_async(self) -> Optional[Dict]:
        try:
            sessions_manager = await MediaManager.request_async()
            sessions = sessions_manager.get_sessions()
            logger.debug(f"Found {len(sessions)} media sessions")

            for session in sessions:
                try:
                    info = session.source_app_user_model_id
                    logger.debug(f"Session app_id: {info}")

                    # Фильтруем только VK, Яндекс, Spotify и т.д.
                    if not any(x in info.lower() for x in ["vk", "yandex", "spotify", "chrome", "firefox", "edge"]):
                        continue

                    media_properties = await session.try_get_media_properties_async()
                    playback_info = session.get_playback_info()
                    timeline = session.get_timeline_properties()

                    is_playing = playback_info.playback_status.value == 3  # 3 = Playing

                    track_info = {
                        "name": media_properties.title,
                        "artist": media_properties.artist,
                        "album": media_properties.album_title,
                        "is_playing": is_playing,
                        "app_name": info,
                        "duration_ms": int(timeline.end_time.total_milliseconds) if timeline.end_time else 0,
                        "progress_ms": int(timeline.position.total_milliseconds) if timeline.position else 0,
                        "image_url": None  # Можно добавить обработку media_properties.thumbnail
                    }
                    logger.info(f"Found track: {track_info['name']} by {track_info['artist']} in {track_info['app_name']}")
                    return track_info
                except Exception as e:
                    logger.error(f"Error processing session: {e}", exc_info=True)
                    continue

            logger.debug("No music track found in any session")
            return None
        except Exception as e:
            logger.error(f"Error getting current track: {e}", exc_info=True)
            return None

    def get_current_track(self) -> Optional[Dict]:
        # Обёртка для синхронного вызова из FastAPI
        return asyncio.run(self.get_current_track_async())

def get_current_track():
    winrt_url = os.environ.get("WINRT_SERVICE_URL", "http://127.0.0.1:8765")
    try:
        resp = requests.get(f"{winrt_url}/current-track", timeout=1)
        return resp.json()
    except Exception:
        return {"error": "winrt service unavailable"} 