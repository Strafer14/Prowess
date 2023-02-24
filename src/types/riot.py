from typing_extensions import TypedDict
from typing import List, Optional, Dict


class GetPuuidResponse(TypedDict):
    puuid: str
    gameName: str
    tagLine: str


class MatchHistory(TypedDict):
    matchId: str
    gameStartTimeMillis: str
    queueId: str


class MatchHistoryResponse(TypedDict):
    puuid: str
    history: List[MatchHistory]


class ErrorStatus(TypedDict):
    message: str
    status_code: int


class RiotResponseFailure(TypedDict):
    status: ErrorStatus


class MatchInfo(TypedDict):
    matchId: str
    mapId: str
    gameVersion: str
    gameLengthMillis: int
    region: str
    gameStartMillis: int
    provisioningFlowId: str
    isCompleted: bool
    customGameName: str
    queueId: str
    gameMode: str
    isRanked: bool
    seasonId: str


class PlayerAbilityCasts(TypedDict):
    grenadeCasts: int
    ability1Casts: int
    ability2Casts: int
    ultimateCasts: int


class PlayerStats(TypedDict):
    score: int
    roundsPlayed: int
    kills: int
    deaths: int
    assists: int
    playtimeMillis: int
    # abilityCasts: PlayerAbilityCasts


class PlayerInfo(TypedDict):
    puuid: str
    gameName: str
    tagLine: str
    teamId: str
    partyId: str
    characterId: str
    stats: PlayerStats
    competitiveTier: int
    isObserver: bool
    playerCard: str
    playerTitle: str


class Team(TypedDict):
    teamId: str
    won: bool
    roundsPlayed: int
    roundsWon: int
    numPoints: int


class Location(TypedDict):
    x: int
    y: int


class PlantPlayerLocation(TypedDict):
    puuid: str
    viewRadians: float
    location: Location


class DamageInfo(TypedDict):
    receiver:  str
    damage: int
    legshots: int
    bodyshots: int
    headshots: int


class EconomyInfo(TypedDict):
    loadoutValue:	int
    weapon:	str
    armor:	str
    remaining:	int
    spent:	int


class PlayerLocation(TypedDict):
    puuid: str
    viewRadians: float
    location: Location


class FinishingDamageInfo(TypedDict):
    damageType: str
    damageItem: str
    isSecondaryFireMode: bool


class KillInfo(TypedDict):
    timeSinceGameStartMillis: int
    timeSinceRoundStartMillis: int
    killer: str
    victim: str
    victimLocation: Location
    assistants: List[str]
    playerLocations: List[PlayerLocation]
    finishingDamage: FinishingDamageInfo


class RoundPlayerStats(TypedDict):
    puuid: str
    kills: List[KillInfo]
    damage: List[DamageInfo]
    score: int
    economy: EconomyInfo
    ability: Dict[str, Optional[str]]


class RoundResult(TypedDict):
    roundNum: int
    roundResult: str
    roundCeremony:  str
    winningTeam: str
    bombPlanter: str
    bombDefuser: Optional[str]
    plantLocation: Location
    plantRoundTime: int
    plantSite: str
    plantPlayerLocations: List[PlantPlayerLocation]
    defuseRoundTime: int
    defusePlayerLocations: Optional[List[int]]
    defuseLocation: Location
    playerStats: List[RoundPlayerStats]
    roundResultCode: str


class MatchResponse(TypedDict):
    matchInfo: MatchInfo
    players: List[PlayerInfo]
    teams: List[Team]
    roundResults: List[RoundResult]
