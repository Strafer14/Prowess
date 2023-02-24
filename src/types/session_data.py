from typing import Optional

from typing_extensions import TypedDict

from src.types.riot import PlayerStats


class ParsedPlayerInfo(TypedDict):
    rank: Optional[int]
    characterId: Optional[str]


class ParsedPlayerAim(TypedDict):
    legshots: int
    bodyshots: int
    headshots: int


class ExtractedMatchMetaData(TypedDict):
    won: int
    gamesPlayed: int
    matchId: Optional[str]
    queueId: Optional[str]
    isCompleted: Optional[bool]
    roundsPlayed: int


class MergedResults(PlayerStats, ParsedPlayerAim):
    pass


class GeneratedMatchResults(TypedDict):
    data: MergedResults
    currentMatchInfo: ExtractedMatchMetaData
    playerInfo: ParsedPlayerInfo


class SessionData(MergedResults):
    won: int
    games_played: int


class Session(TypedDict):
    sessionId: str
    currentMatchInfo: ExtractedMatchMetaData
    playerInfo: ParsedPlayerInfo
    puuid: str
    region: str
    data: SessionData
