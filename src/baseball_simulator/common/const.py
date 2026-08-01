from __future__ import annotations

TOTAL_GAME_NUMBER: int = 143
OPPOSITE_TEAM_LIST: list[str] = [
    "Fighters",
    "Buffaloes",
    "Eagles",
    "Lions",
    "Marines",
]

# 平均能力値
SPEED_PITCHER_AVG: float = 145.0
BREAKING_BALL_AVG: float = 7.0
MEET_AVG: float = 50.0
POWER_AVG: float = 50.0
SPEED_BATTER_AVG: float = 50.0
TRAJECTORY_AVG: float = 2.0

# 特殊能力・ランク補正マッピング
# 野手用ランク補正 (ランク: (ミート補正, パワー補正))
BATTER_RANK_MAP: dict[str, tuple[int, int]] = {
    "A": (15, 10),
    "B": (8, 5),
    "C": (5, 2),
    "D": (0, 0),
    "E": (-5, -2),
    "F": (-8, -5),
    "G": (-15, -10),
}

# 対ピンチ補正 (ランク: (球速, 制球, 変化球))
PITCHER_RISP_MAP: dict[str, tuple[int, int, int]] = {
    "A": (2, 0, 4),
    "B": (1, 0, 2),
    "C": (1, 0, 0),
    "D": (0, 0, 0),
    "E": (-1, 0, 0),
    "F": (-1, 0, -2),
    "G": (-2, 0, -4),
}

# 対左打者補正 (ランク: (球速, 制球, 変化球))
PITCHER_LEFT_MAP: dict[str, tuple[int, int, int]] = {
    "A": (6, 12, 0),
    "B": (4, 10, 0),
    "C": (2, 4, 0),
    "D": (0, 0, 0),
    "E": (-2, 4, 0),
    "F": (-4, -10, -2),
    "G": (-6, -12, -4),
}

# ノビ補正(ランク: (球速))
PITCHER_NOBI_MAP: dict[str, int] = {
    "A": 8,
    "B": 4,
    "C": 2,
    "D": 0,
    "E": -2,
    "F": -4,
    "G": -8,
}

# 回復・疲労用定数
RECOVERY_MAP: dict[str, int] = {
    "A": 40,
    "B": 35,
    "C": 30,
    "D": 25,
    "E": 20,
    "F": 15,
    "G": 10,
}

POS_FATIGUE_MAP: dict[str, float] = {
    "捕": 2.0,
    "遊": 1.7,
    "二": 1.5,
    "中": 1.2,
    "三": 1.1,
    "右": 1.0,
    "一": 1.0,
    "左": 0.8,
    "指": 0.6,
}

# 打撃・打球判定マッピング
# 弾道別の打球種類確率マップ [ゴロ(GB), ライナー(LD), 内野フライ(IFFB), 外野フライ(OFFB)]
TRAJECTORY_MAP: dict[int, tuple[int, int, int, int]] = {
    1: (600, 200, 150, 50),
    2: (450, 300, 100, 150),
    3: (300, 350, 50, 300),
    4: (200, 300, 20, 480),
}

# 方向×打球種類ごとのベース安打確率マップ (1000分率)
BATTING_RESULT_MAP: dict[str, dict[str, dict[str, float]]] = {
    "PULL": {
        "GB": {"1B": 150, "2B": 20, "3B": 0, "HR": 0},
        "LD": {"1B": 350, "2B": 120, "3B": 5, "HR": 30},
        "IFFB": {"1B": 10, "2B": 0, "3B": 0, "HR": 0},
        "OFFB": {"1B": 80, "2B": 100, "3B": 10, "HR": 80},
    },
    "CENT": {
        "GB": {"1B": 180, "2B": 10, "3B": 0, "HR": 0},
        "LD": {"1B": 400, "2B": 80, "3B": 10, "HR": 20},
        "IFFB": {"1B": 10, "2B": 0, "3B": 0, "HR": 0},
        "OFFB": {"1B": 120, "2B": 80, "3B": 15, "HR": 60},
    },
    "OPPO": {
        "GB": {"1B": 140, "2B": 15, "3B": 0, "HR": 0},
        "LD": {"1B": 320, "2B": 100, "3B": 5, "HR": 10},
        "IFFB": {"1B": 10, "2B": 0, "3B": 0, "HR": 0},
        "OFFB": {"1B": 100, "2B": 70, "3B": 5, "HR": 30},
    },
}
