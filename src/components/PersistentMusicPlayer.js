import React, { useState, useEffect } from 'react';
import {
    Box,
    Paper,
    Typography,
    IconButton,
    Slider,
    Tooltip,
    Avatar,
    styled,
    Fab
} from '@mui/material';
import {
    PlayArrow as PlayArrowIcon,
    Pause as PauseIcon,
    SkipNext as SkipNextIcon,
    SkipPrevious as SkipPreviousIcon,
    DragIndicator as DragIndicatorIcon,
    MusicNote as MusicNoteIcon,
    Close as CloseIcon
} from '@mui/icons-material';
import Draggable from 'react-draggable';

const PlayerContainer = styled(Paper)(({ theme }) => ({
    position: 'fixed',
    bottom: 20,
    right: 20,
    width: 300,
    backgroundColor: theme.palette.background.paper,
    borderRadius: 8,
    boxShadow: theme.shadows[3],
    padding: theme.spacing(2),
    zIndex: 1000,
    cursor: 'move',
    '&:hover': {
        boxShadow: theme.shadows[6],
    },
}));

const DragHandle = styled(DragIndicatorIcon)(({ theme }) => ({
    cursor: 'move',
    position: 'absolute',
    top: 8,
    right: 8,
    color: theme.palette.text.secondary,
}));

const PlayerContent = styled(Box)(({ theme }) => ({
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing(1),
}));

const TrackInfo = styled(Box)(({ theme }) => ({
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing(1),
}));

const Controls = styled(Box)(({ theme }) => ({
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
}));

const ToggleButton = styled(Fab)(({ theme }) => ({
    position: 'fixed',
    bottom: 20,
    right: 20,
    zIndex: 1000,
    backgroundColor: theme.palette.primary.main,
    '&:hover': {
        backgroundColor: theme.palette.primary.dark,
    },
}));

const formatTime = (ms) => {
    if (!ms) return '0:00';
    const totalSeconds = Math.floor(ms / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
};

const PersistentMusicPlayer = () => {
    const [position, setPosition] = useState({ x: 0, y: 0 });
    const [currentTrack, setCurrentTrack] = useState(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [isVisible, setIsVisible] = useState(false);
    const [prevTrackId, setPrevTrackId] = useState(null);
    const POLL_INTERVAL = 2000; // Increase polling interval to 2 seconds

    const getTrackId = (track) => {
        if (!track) return null;
        return `${track.name || ''}__${track.artist || ''}`;
    };

    useEffect(() => {
        const pollInterval = setInterval(async () => {
            try {
                const response = await fetch('/api/music/current-track');
                const data = await response.json();
                if (data && !data.error) {
                    setCurrentTrack(data);
                    if (!isVisible) {
                        setIsVisible(true);
                    }
                    const newTrackId = getTrackId(data);
                    if (prevTrackId !== newTrackId) {
                        setIsPlaying(data.is_playing);
                        setPrevTrackId(newTrackId);
                    } else {
                        if (isPlaying !== data.is_playing) {
                            setIsPlaying(data.is_playing);
                        }
                    }
                } else {
                    setCurrentTrack(null);
                    setIsPlaying(false);
                    setPrevTrackId(null);
                }
            } catch (error) {
                console.error('Error fetching current track:', error);
            }
        }, POLL_INTERVAL);

        return () => clearInterval(pollInterval);
    }, [isVisible, prevTrackId, isPlaying]);

    const handleDragStop = (e, data) => {
        setPosition({ x: data.x, y: data.y });
    };

    const handlePlayPause = async () => {
        try {
            const response = await fetch('/api/music/playback-state', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    is_playing: !isPlaying
                })
            });
            if (response.ok) {
                const data = await response.json();
                if (data.status === 'success') {
                    setIsPlaying(!isPlaying);
                }
            }
        } catch (error) {
            console.error('Error toggling playback:', error);
        }
    };

    const handleSkipNext = async () => {
        try {
            await fetch('/api/music/skip-next', {
                method: 'POST',
            });
        } catch (error) {
            console.error('Error skipping to next track:', error);
        }
    };

    const handleSkipPrevious = async () => {
        try {
            await fetch('/api/music/skip-previous', {
                method: 'POST',
            });
        } catch (error) {
            console.error('Error skipping to previous track:', error);
        }
    };

    return (
        <>
            {!isVisible && (
                <ToggleButton
                    color="primary"
                    onClick={() => setIsVisible(true)}
                    size="medium"
                >
                    <MusicNoteIcon />
                </ToggleButton>
            )}
            
            {isVisible && (
                <Draggable
                    handle=".drag-handle"
                    bounds="parent"
                    position={position}
                    onStop={(e, data) => setPosition({ x: data.x, y: data.y })}
                >
                    <PlayerContainer>
                        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
                            <IconButton
                                size="small"
                                onClick={() => setIsVisible(false)}
                                sx={{ position: 'absolute', top: 4, right: 4 }}
                            >
                                <CloseIcon fontSize="small" />
                            </IconButton>
                            <DragHandle className="drag-handle" />
                        </Box>
                        
                        <PlayerContent>
                            <TrackInfo>
                                {currentTrack?.image_url && (
                                    <Avatar
                                        src={currentTrack.image_url}
                                        alt={currentTrack?.name}
                                        variant="rounded"
                                        sx={{ width: 48, height: 48 }}
                                    />
                                )}
                                <Box sx={{ flex: 1, minWidth: 0 }}>
                                    <Typography variant="subtitle1" noWrap>
                                        {currentTrack?.name ? currentTrack.name : 'Нет активного трека'}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary" noWrap>
                                        {currentTrack?.artist ? currentTrack.artist : 'Выберите музыку для воспроизведения'}
                                    </Typography>
                                </Box>
                            </TrackInfo>

                            <Controls>
                                <Box>
                                    <IconButton size="small" disabled={!currentTrack} onClick={handleSkipPrevious}>
                                        <SkipPreviousIcon />
                                    </IconButton>
                                    <IconButton 
                                        onClick={handlePlayPause}
                                        disabled={!currentTrack}
                                    >
                                        {isPlaying ? <PauseIcon /> : <PlayArrowIcon />}
                                    </IconButton>
                                    <IconButton size="small" disabled={!currentTrack} onClick={handleSkipNext}>
                                        <SkipNextIcon />
                                    </IconButton>
                                </Box>
                            </Controls>
                        </PlayerContent>
                    </PlayerContainer>
                </Draggable>
            )}
        </>
    );
};

export default PersistentMusicPlayer; 