import random
from enum import Enum, auto

from baseball_simulator.data_model.data_model import Player

# 定数値（平均能力値）
SPEED_PITCHER_AVG = 145.0
BREAKING_BALL_AVG = 7.0
MEET_AVG = 50.0
POWER_AVG = 50.0
SPEED_BATTER_AVG = 50.0
TRAJECTORY_AVG = 2.0

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


class AtBatResult(Enum):
    """打席結果の種類"""

    OUT = auto()
    STRIKEOUT = auto()
    WALK = auto()
    HIT_BY_PITCH = auto()
    SINGLE = auto()
    DOUBLE = auto()
    TRIPLE = auto()
    HOME_RUN = auto()


RESULT_CONVERT_MAP = {
    "SO": AtBatResult.STRIKEOUT,
    "BB": AtBatResult.WALK,
    "HBP": AtBatResult.HIT_BY_PITCH,
    "1B": AtBatResult.SINGLE,
    "2B": AtBatResult.DOUBLE,
    "3B": AtBatResult.TRIPLE,
    "HR": AtBatResult.HOME_RUN,
    "OUT": AtBatResult.OUT,
}


def _choice_by_weight(weights: list[tuple[str, float]]) -> str | None:
    """
    [(結果名, 確率重み), ...] のリストを受け取り、1000分率の乱数判定で選択された結果を返す。
    どの条件にも引っかからなかった場合は None を返す。
    """
    num = random.randrange(1000)
    current_weight = 0.0
    for label, weight in weights:
        current_weight += weight
        if num <= current_weight:
            return label
    return None


def determine_at_bat_result(pitcher: Player, batter: Player) -> AtBatResult:
    """投手の能力（調子・疲労含む）と打者の能力（調子・疲労含む）から1打席の結果を判定する"""
    assert pitcher.pitcher is not None
    assert batter.batter is not None

    p_ability = pitcher.pitcher.ability.basic_ability
    b_ability = batter.batter.ability.basic_ability
    b_special = batter.batter.ability.special_ability

    # 投手の調子・疲労補正計算
    p_condition_corr = _pitcher_condition_correction(pitcher.barometer.condition)
    p_fatigue_debuff = pitcher.barometer.accumulates_fatigue / 100.0

    velocity = (
        p_ability.velocity + p_condition_corr["velocity"] - (3.0 * p_fatigue_debuff)
    )
    control = (
        p_ability.control + p_condition_corr["control"] - (10.0 * p_fatigue_debuff)
    )
    breaking_ball = (
        p_ability.breaking_ball_level
        + p_condition_corr["breaking_ball"]
        - (1.5 * p_fatigue_debuff)
    )

    # 投手能力が打者能力に与える補正計算
    meet_pitcher_corr, power_pitcher_corr = _pitcher_ability_correction(
        velocity, control, breaking_ball
    )

    # 野手の調子・疲労補正計算
    b_condition_corr = _batter_condition_correction(batter.barometer.condition)
    b_fatigue_debuff = batter.barometer.accumulates_fatigue / 100.0

    meet = (
        b_ability.meet
        + meet_pitcher_corr
        + b_condition_corr["meet"]
        - (5.0 * b_fatigue_debuff)
    )
    power = (
        b_ability.power
        + power_pitcher_corr
        + b_condition_corr["power"]
        - (5.0 * b_fatigue_debuff)
    )
    speed_b = b_ability.speed - (5.0 * b_fatigue_debuff)
    eye = b_special.eye

    str_result = _result_logic(
        trajectory=b_ability.trajectory,
        meet=meet,
        power=power,
        speed_b=speed_b,
        eye=eye,
        velocity=velocity,
        control=control,
        breaking_ball=breaking_ball,
    )

    return RESULT_CONVERT_MAP[str_result]


def _pitcher_condition_correction(condition: int) -> dict[str, float]:
    """投手の調子による能力補正（絶好調:2 〜 絶不調:-2）"""
    return {
        "velocity": condition * 1.0,
        "control": condition * 3.0,
        "breaking_ball": condition * 0.5,
    }


def _batter_condition_correction(condition: int) -> dict[str, float]:
    """野手の調子による能力補正（絶好調:2 〜 絶不調:-2）"""
    return {
        "meet": condition * 3.0,
        "power": condition * 3.0,
    }


def _pitcher_ability_correction(
    velocity: float, control: float, breaking_ball: float
) -> tuple[float, float]:
    """投手の基礎能力から打者への抑え込み補正を算出"""
    meet_corr = -(control - MEET_AVG) * 0.2 - (breaking_ball - BREAKING_BALL_AVG) * 2.0
    power_corr = (
        -(velocity - SPEED_PITCHER_AVG) * 0.3
        - (breaking_ball - BREAKING_BALL_AVG) * 1.5
    )
    return meet_corr, power_corr


def _eye_logic(eye: str) -> float:
    """選球眼ランク（A~G等）に応じた補正値"""
    eye_map = {
        "A": 80.0,
        "B": 70.0,
        "C": 60.0,
        "D": 50.0,
        "E": 40.0,
        "F": 30.0,
        "G": 20.0,
    }
    return eye_map.get(eye.upper(), 40.0)


def _result_logic(
    trajectory: int,
    meet: float,
    power: float,
    speed_b: float,
    eye: str,
    velocity: float,
    control: float,
    breaking_ball: float,
) -> str:
    """打席結果判定処理"""

    # 打球が発生しないイベント（三振・四球・死球）
    swing_out_per = (
        125
        + (velocity - SPEED_PITCHER_AVG)
        + (breaking_ball - BREAKING_BALL_AVG) * 3
        + (meet - MEET_AVG) * (-5)
    )

    walk_per = (
        -15
        + (trajectory * 30) // 4
        + (power * 80 - speed_b * 10) // 50
        - random.randrange(24)
        + random.randrange(32)
    )
    walk_per += (_eye_logic(eye) - control) * 1.5

    non_batting_result = _choice_by_weight(
        [
            ("SO", swing_out_per),
            ("BB", walk_per),
            ("HBP", 10),
        ]
    )
    if non_batting_result:
        return non_batting_result

    # 打球角度判定
    gb, ld, iffb, offb = TRAJECTORY_MAP.get(trajectory, TRAJECTORY_MAP[2])
    trajectory_result = (
        _choice_by_weight(
            [
                ("GB", gb),
                ("LD", ld),
                ("IFFB", iffb),
                ("OFFB", offb),
            ]
        )
        or "GB"
    )

    # 打球方向判定
    batting_power = meet * 0.5 + power
    pull_per = ((1 / 450) * batting_power + (7 / 30)) * 1000
    center_per = (-(1 / 900) * batting_power + (13 / 30)) * 1000

    direction_result = (
        _choice_by_weight(
            [
                ("PULL", pull_per),
                ("CENT", center_per),
            ]
        )
        or "OPPO"
    )

    # 打球結果判定
    probs = BATTING_RESULT_MAP[direction_result][trajectory_result]
    result = (
        _choice_by_weight(
            [
                ("1B", probs["1B"] / 0.72),
                ("2B", probs["2B"] / 0.72),
                ("3B", probs["3B"] / 0.72),
                ("HR", probs["HR"] / 0.72),
            ]
        )
        or "OUT"
    )

    # 成績補正（結果の上書き判定）
    if result == "OUT":
        sc_per = max(0.0, (meet - MEET_AVG) * 2 + (speed_b - SPEED_BATTER_AVG))
        dc_per = max(0.0, (power - POWER_AVG) * 0.25)
        hr_per = max(0.0, (power - POWER_AVG) * 2 + (trajectory - TRAJECTORY_AVG) * 10)
        return (
            _choice_by_weight(
                [
                    ("1B", sc_per),
                    ("2B", dc_per),
                    ("HR", hr_per),
                ]
            )
            or "OUT"
        )

    elif result == "1B":
        dc_per = max(0.0, (power - POWER_AVG) * 0.25 + (speed_b - SPEED_BATTER_AVG) * 2)
        hr_per = max(0.0, (power - POWER_AVG) * 3)
        return (
            _choice_by_weight(
                [
                    ("2B", dc_per),
                    ("HR", hr_per),
                ]
            )
            or "1B"
        )

    elif result == "2B":
        tc_per = max(0.0, (speed_b - SPEED_BATTER_AVG) * 8)
        hr_per = max(0.0, (power - POWER_AVG) * 4 + (trajectory - TRAJECTORY_AVG) * 15)
        return (
            _choice_by_weight(
                [
                    ("3B", tc_per),
                    ("HR", hr_per),
                ]
            )
            or "2B"
        )

    return result
