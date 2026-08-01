from dataclasses import dataclass

from baseball_simulator.data_model.data_model import Player, Team


@dataclass
class StartingLineup:
    """1試合におけるチームのスタメン・打順・守備位置情報"""

    team: Team
    starter_pitcher: Player  # 先発投手
    lineup: list[Player]  # 打順順（1番〜9番）の Player リスト
    positions: dict[Player, str]  # 選手ごとの守備位置マップ ("捕", "一", "指" など)


@dataclass
class GameState:
    """1試合の進行状態を保持するモデル"""

    home_lineup: StartingLineup  # ホームチームのラインナップ
    away_lineup: StartingLineup  # ビジターチームのラインナップ
    inning: int = 1  # イニング（1回〜）
    is_top: bool = True  # 表（True）/ 裏（False）
    home_score: int = 0  # ホーム得点
    away_score: int = 0  # ビジター得点
    out_count: int = 0  # アウトカウント (0〜2)
