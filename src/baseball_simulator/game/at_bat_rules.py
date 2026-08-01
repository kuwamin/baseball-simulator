import random
from enum import Enum, auto

from baseball_simulator.data_model.data_model import Player


class AtBatResult(Enum):
    """打席結果の種類"""

    OUT = auto()  # 凡打・ライナー等（アウト）
    STRIKEOUT = auto()  # 三振
    WALK = auto()  # 四球（フォアボール）
    SINGLE = auto()  # 単打（ヒット）
    DOUBLE = auto()  # 二塁打
    TRIPLE = auto()  # 三塁打
    HOME_RUN = auto()  # 本塁打（ホームラン）


def determine_at_bat_result(pitcher: Player, batter: Player) -> AtBatResult:
    """投手の能力と打者の能力から1打席の結果を判定する（まずはシンプル実装）"""
    # 型チェックガード（将来的に能力値を参照する際のため）
    assert pitcher.pitcher is not None
    assert batter.batter is not None

    # 1. 乱数を用いたシンプルな確率分岐（動作確認用）
    rand_val = random.random()

    if rand_val < 0.15:
        return AtBatResult.STRIKEOUT  # 15% で三振
    elif rand_val < 0.25:
        return AtBatResult.WALK  # 10% で四球
    elif rand_val < 0.45:
        return AtBatResult.SINGLE  # 20% で単打
    elif rand_val < 0.50:
        return AtBatResult.DOUBLE  # 5% で二塁打
    elif rand_val < 0.51:
        return AtBatResult.TRIPLE  # 1% で三塁打
    elif rand_val < 0.54:
        return AtBatResult.HOME_RUN  # 3% でホームラン
    else:
        return AtBatResult.OUT  # 46% で凡打（アウト）
