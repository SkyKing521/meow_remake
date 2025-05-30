import asyncio
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import winrt.windows.media.control as wmc
from winrt.windows.foundation import TimeSpan
from typing import Dict, Any, Optional
import httpx
import time
from datetime import datetime, timedelta
import os
import logging
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
REQUEST_TIMEOUT = 10.0  # seconds
WINRT_OPERATION_TIMEOUT = 30.0  # seconds

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting WinRT service...")
    try:
        # Create a persistent HTTP client with increased timeout
        app.state.http_client = httpx.AsyncClient(timeout=REQUEST_TIMEOUT)
        yield
    finally:
        # Shutdown
        logger.info("Shutting down WinRT service...")
        await app.state.http_client.aclose()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store the last active session ID
last_active_session_id = None

# Get service URL from environment
winrt_service_url = os.environ.get("WINRT_SERVICE_URL", "http://26.34.237.219:8765")

# Helper function to convert TimeSpan to milliseconds (more robust)
def timespan_to_ms(timespan):
    try:
        # Check if timespan has the expected structure
        if timespan and hasattr(timespan, 'duration') and hasattr(timespan.duration, 'total_seconds'):
            return int(timespan.duration.total_seconds() * 1000)
        else:
            return 0
    except Exception as e:
        print(f"Error converting timespan {timespan} (type: {type(timespan)}): {e}")
        return 0

async def get_session_by_id(sessions_manager, session_id):
    """Get a specific session by its ID"""
    sessions = sessions_manager.get_sessions()
    for session in sessions:
        if session.source_app_user_model_id == session_id:
            return session
    return None

async def get_media_session_with_timeout():
    """Get media session with timeout handling"""
    try:
        sessions_manager = await asyncio.wait_for(wmc.GlobalSystemMediaTransportControlsSessionManager.request_async(), timeout=WINRT_OPERATION_TIMEOUT)
        return sessions_manager.get_current_session()
    except asyncio.TimeoutError:
        logger.error("Timeout while getting media session")
        raise HTTPException(status_code=503, detail="Media session request timed out")
    except Exception as e:
        logger.error(f"Error getting media session: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting media session: {str(e)}")

@app.get("/current-track")
async def get_current_track(request: Request):
    global last_active_session_id
    try:
        # Check if client is still connected
        if await request.is_disconnected():
            logger.info("Client disconnected, cancelling request")
            return

        current_session = await get_media_session_with_timeout()

        logger.debug(f"Current session after get_media_session_with_timeout: {current_session}")

        # If we have a last active session, try to find it
        if last_active_session_id and current_session:
            if current_session.source_app_user_model_id == last_active_session_id:
                # Last active session is still current, use it
                pass # current_session remains the same
            else:
                # Current session ID is different from last active. Update last active.
                last_active_session_id = current_session.source_app_user_model_id

        if current_session:
            # Update last active session ID if it was None before or updated above
            if last_active_session_id is None:
                 last_active_session_id = current_session.source_app_user_model_id

            try:
                logger.debug("Attempting to get media properties...")
                media_properties = await asyncio.wait_for(current_session.try_get_media_properties_async(), timeout=WINRT_OPERATION_TIMEOUT)
                logger.debug(f"Successfully got media properties: {media_properties}")

                logger.debug("Attempting to get playback info...")
                playback_info = current_session.get_playback_info()
                logger.debug(f"Successfully got playback info: {playback_info}")

                logger.debug("Attempting to get timeline properties...")
                timeline_properties = current_session.get_timeline_properties()
                logger.debug(f"Successfully got timeline properties: {timeline_properties}")

                is_playing = (playback_info.playback_status == wmc.GlobalSystemMediaTransportControlsSessionPlaybackStatus.PLAYING)
                duration_ms = timespan_to_ms(timeline_properties.end_time)
                progress_ms = timespan_to_ms(timeline_properties.position)

                logger.info(f"Fetched Track Info: "
                      f"Name: {media_properties.title}, Artist: {media_properties.artist}, "
                      f"App: {current_session.source_app_user_model_id}, IsPlaying: {is_playing}, "
                      f"Progress: {progress_ms}ms, Duration: {duration_ms}ms")

                return {
                    "name": media_properties.title,
                    "artist": media_properties.artist,
                    "album": media_properties.album_title,
                    "app_name": current_session.source_app_user_model_id,
                    "is_playing": is_playing,
                    "duration_ms": duration_ms,
                    "progress_ms": progress_ms,
                    "image_url": None,
                }
            except asyncio.TimeoutError:
                logger.error("Timeout while getting media properties", exc_info=True)
                raise HTTPException(status_code=503, detail="Media properties request timed out")
            except Exception as e:
                logger.error(f"Error getting media properties: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error getting media properties: {str(e)}")
        else:
            logger.info("No active media session found")
            return {"name": None, "artist": None, "album": None, "app_name": None, 
                   "is_playing": False, "duration_ms": 0, "progress_ms": 0, "image_url": None}
    except asyncio.CancelledError:
        logger.info("Request cancelled")
        raise

@app.put("/playback-state")
async def update_playback_state(state: Dict[str, bool]):
    try:
        sessions_manager = await wmc.GlobalSystemMediaTransportControlsSessionManager.request_async()
        current_session = sessions_manager.get_current_session()

        if current_session:
            is_playing_state = state.get("is_playing")
            print(f"[WinRT Service] Received playback state update: is_playing={is_playing_state}")
            
            try:
                if is_playing_state is True:
                    await current_session.try_play_async()
                    print("[WinRT Service] Called try_play_async()")
                elif is_playing_state is False:
                    await current_session.try_pause_async()
                    print("[WinRT Service] Called try_pause_async()")
                
                # Verify the state change
                playback_info = current_session.get_playback_info()
                actual_state = (playback_info.playback_status == wmc.GlobalSystemMediaTransportControlsSessionPlaybackStatus.PLAYING)
                if actual_state == is_playing_state:
                    return {"status": "success"}
                else:
                    print(f"[WinRT Service] State verification failed. Expected: {is_playing_state}, Got: {actual_state}")
                    return {"status": "error", "message": "State change verification failed"}
            except Exception as e:
                print(f"[WinRT Service] Error during playback state change: {e}")
                raise HTTPException(status_code=500, detail=f"Error during playback state change: {e}")
        else:
            print("[WinRT Service] No active media session to update playback state.")
            raise HTTPException(status_code=404, detail="No active media session")
    except Exception as e:
        print(f"[WinRT Service] Error updating playback state: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating playback state: {e}")

@app.post("/skip-next")
async def skip_next_track():
    try:
        sessions_manager = await wmc.GlobalSystemMediaTransportControlsSessionManager.request_async()
        current_session = sessions_manager.get_current_session()

        if current_session:
            print("[WinRT Service] Received skip next command.")
            await current_session.try_skip_next_async()
            print("[WinRT Service] Called try_skip_next_async().")
            return {"status": "success"}
        else:
            print("[WinRT Service] No active media session to skip next.")
            raise HTTPException(status_code=404, detail="No active media session")
    except Exception as e:
        print(f"Error skipping next track: {e}")
        raise HTTPException(status_code=500, detail=f"Error skipping next track: {e}")

@app.post("/skip-previous")
async def skip_previous_track():
    try:
        sessions_manager = await wmc.GlobalSystemMediaTransportControlsSessionManager.request_async()
        current_session = sessions_manager.get_current_session()

        if current_session:
            print("[WinRT Service] Received skip previous command.")
            await current_session.try_skip_previous_async()
            print("[WinRT Service] Called try_skip_previous_async().")
            return {"status": "success"}
        else:
            print("[WinRT Service] No active media session to skip previous.")
            raise HTTPException(status_code=404, detail="No active media session")
    except Exception as e:
        print(f"Error skipping previous track: {e}")
        raise HTTPException(status_code=500, detail=f"Error skipping previous track: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8765, 
        reload=True,
        timeout_keep_alive=30,
        timeout_graceful_shutdown=10
    )