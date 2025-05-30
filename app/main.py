from app.services.spotify_service import SpotifyService
from app.services.media_session_service import MediaSessionService, get_current_track

# Инициализация Spotify сервиса
spotify_service = SpotifyService()

# Initialize media session service
media_session_service = MediaSessionService()

@app.get("/api/spotify/current-track")
async def get_current_track():
    """
    Получает информацию о текущем воспроизводимом треке в Spotify
    """
    track_info = spotify_service.get_current_track()
    if track_info:
        return track_info
    return {"error": "No track currently playing"}

@app.get("/api/spotify/playback-state")
async def get_playback_state():
    """
    Получает текущее состояние воспроизведения в Spotify
    """
    state = spotify_service.get_playback_state()
    if state:
        return state
    return {"error": "No playback state available"}

@app.get("/api/music/current-track")
def get_current_track_endpoint():
    return get_current_track()

@app.put("/api/music/playback-state")
async def update_playback_state(is_playing: bool):
    """
    Update the playback state (play/pause) of the current music application
    """
    success = media_session_service.update_playback_state(is_playing)
    if success:
        return {"status": "success"}
    return {"error": "Failed to update playback state"} 