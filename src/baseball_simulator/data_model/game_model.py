from dataclasses import dataclass, field

from baseball_simulator.data_model.data_model import Player, Team


@dataclass
class Bases:
    """各塁の走者状態を保持するクラス"""

    first: Player | None = None
    second: Player | None = None
    third: Player | None = None

    def clear(self) -> None:
        """チェンジ時に塁をリセット"""
        self.first = None
        self.second = None
        self.third = None


@dataclass
class StartingLineup:
    team: Team
    starter_pitcher: Player
    lineup: list[Player]
    positions: dict[Player, str]


@dataclass
class GameState:
    home_lineup: StartingLineup
    away_lineup: StartingLineup
    inning: int = 1
    is_top: bool = True
    home_score: int = 0
    away_score: int = 0
    out_count: int = 0

    away_batter_index: int = 0
    home_batter_index: int = 0

    # 塁の状態を追加
    bases: Bases = field(default_factory=Bases)

    is_game_over: bool = False

    def get_current_batter(self) -> Player:
        """現在打席に立っている打者（野手の Player オブジェクト）を取得"""
        if self.is_top:
            return self.away_lineup.lineup[self.away_batter_index]
        return self.home_lineup.lineup[self.home_batter_index]

    def get_current_pitcher(self) -> Player:
        """現在マウンドに立っている守備側の投手（投手の Player オブジェクト）を取得"""
        if self.is_top:
            return self.home_lineup.starter_pitcher  # 表は Home が守備
        return self.away_lineup.starter_pitcher  # 裏は Away が守備

    def advance_next_batter(self) -> None:
        """次の打者へインデックスを進める (0〜8の循環)"""
        if self.is_top:
            self.away_batter_index = (self.away_batter_index + 1) % 9
        else:
            self.home_batter_index = (self.home_batter_index + 1) % 9

    def add_score(self, runs: int) -> None:
        """攻撃側のスコアを加算"""
        if self.is_top:
            self.away_score += runs
        else:
            self.home_score += runs

    def change_possession(self) -> None:
        """チェンジ（攻守交代）処理"""
        self.out_count = 0
        self.bases.clear()  # チェンジ時に走者をクリア

        if self.is_top:
            self.is_top = False
        else:
            self.is_top = True
            self.inning += 1

        if self.inning > 9:
            self.is_game_over = True
