from dataclasses import dataclass, field


# 1. 共通 / 基本情報モデル (Common Models)
@dataclass
class CommonInformation:
    number: str
    dominant_hitting: int
    dominant_arm: int
    name: str


@dataclass
class Barometer:
    accumulates_fatigue: int = 0
    condition: int = 0


@dataclass
class CommonSpecialAbility:
    injury_res: int
    recovery: int


@dataclass
class CommonStats:
    games: int = 0


# 2. 投手モデル (Pitcher Models)
@dataclass
class PitcherBasicAbility:
    velocity: int
    control: int
    stamina: int
    breaking_ball_level: int
    breaking_ball_number: int


@dataclass
class PitcherSpecialAbility:
    clutch_pitching: int
    vs_left_batter: int
    quick: int
    fastball_life: int
    toughness: int
    common_special_ability: CommonSpecialAbility


@dataclass
class PitcherAbility:
    basic_ability: PitcherBasicAbility
    special_ability: PitcherSpecialAbility


@dataclass
class PitcherStats:
    starter: int = 0
    wins: int = 0
    losses: int = 0
    saves: int = 0
    holds: int = 0
    outs: int = 0
    completes: int = 0
    shutouts: int = 0
    bf: int = 0
    strikeouts: int = 0
    walks_allowed: int = 0
    hbp_allowed: int = 0
    hr_allowed: int = 0
    hits_allowed: int = 0
    run_allowed: int = 0
    earned_run: int = 0
    qs: int = 0
    hqs: int = 0
    risp_batter_faces: int = 0
    risp_hit_allowed: int = 0
    common_stats: CommonStats = field(default_factory=CommonStats)


@dataclass
class Pitcher:
    aptitude: int
    ability: PitcherAbility
    fatugue_stamina: int = 0
    stats: PitcherStats = field(default_factory=PitcherStats)


# 3. 野手モデル (Batter Models)
@dataclass
class BatterBasicAbility:
    trajectory: int
    meet: int
    power: int
    speed: int
    arm: int
    fielding: int
    catching: int


@dataclass
class BatterSpecialAbility:
    clutch_batting: int
    vs_left_pitcher: int
    stealing: int
    base_running: int
    throwing: int
    eye: int
    common_special_ability: CommonSpecialAbility


@dataclass
class BatterAbility:
    basic_ability: BatterBasicAbility
    special_ability: BatterSpecialAbility


@dataclass
class BatterStats:
    pa: int = 0
    ab: int = 0
    singles: int = 0
    doubles: int = 0
    triples: int = 0
    homerun: int = 0
    rbi: int = 0
    walks: int = 0
    hbp: int = 0
    so: int = 0
    sac_bunt: int = 0
    sac_fly: int = 0
    steals: int = 0
    caught_stealing: int = 0
    gdp: int = 0
    risp_ab: int = 0
    risp_hits: int = 0
    common_stats: CommonStats = field(default_factory=CommonStats)


@dataclass
class Batter:
    position: int
    ability: BatterAbility
    stats: BatterStats = field(default_factory=BatterStats)


# 4. 選手・チームモデル (Player / Team Models)
@dataclass
class Player:
    player_info: CommonInformation
    barometer: Barometer = field(default_factory=Barometer)
    pitcher: Pitcher | None = None
    batter: Batter | None = None

    def __post_init__(self) -> None:
        """初期化直後に {xor} 制約（どちらか片方のみが存在する）を検証する"""
        if (self.pitcher is None and self.batter is None) or (
            self.pitcher is not None and self.batter is not None
        ):
            raise ValueError("Player must have either Pitcher or Batter role (XOR).")


@dataclass
class Team:
    team_name: str
    players: list[Player] = field(default_factory=list)
