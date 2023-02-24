from typing_extensions import TypedDict
from typing import Dict, Any


class SessionData(TypedDict):
    score: int
    roundsPlayed: int
    kills: int
    deaths: int
    assists: int
    playtimeMillis: int
    legshots: int
    bodyshots: int
    headshots: int
    won: int
    games_played: int


class Session(TypedDict):
    sessionId: str
    currentMatchInfo: Dict[str, Any]
    playerInfo: Dict[str, Any]
    puuid: str
    region: str
    data: SessionData
