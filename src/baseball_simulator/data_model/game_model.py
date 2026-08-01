from dataclasses import dataclass

from baseball_simulator.data_model.data_model import Player, Team


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
    is_top: bool = True  # True: 表（Away攻撃/Home守備）, False: 裏（Home攻撃/Away守備）
    home_score: int = 0
    away_score: int = 0
    out_count: int = 0

    away_batter_index: int = 0
    home_batter_index: int = 0

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

    def change_possession(self) -> None:
        """チェンジ（攻守交代）処理"""
        self.out_count = 0

        if self.is_top:
            self.is_top = False
        else:
            self.is_top = True
            self.inning += 1

        if self.inning > 9:
            self.is_game_over = True
