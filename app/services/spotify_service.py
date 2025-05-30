import os
from typing import Optional, Dict
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

class SpotifyService:
    def __init__(self):
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:8000/callback')
        self.scope = 'user-read-currently-playing user-read-playback-state'
        
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope
        ))

    def get_current_track(self) -> Optional[Dict]:
        """
        Получает информацию о текущем воспроизводимом треке
        """
        try:
            current = self.sp.current_playback()
            if current and current.get('item'):
                track = current['item']
                return {
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album': track['album']['name'],
                    'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'is_playing': current['is_playing'],
                    'progress_ms': current['progress_ms'],
                    'duration_ms': track['duration_ms']
                }
        except Exception as e:
            print(f"Error getting current track: {e}")
            return None

    def get_playback_state(self) -> Optional[Dict]:
        """
        Получает текущее состояние воспроизведения
        """
        try:
            return self.sp.current_playback()
        except Exception as e:
            print(f"Error getting playback state: {e}")
            return None 