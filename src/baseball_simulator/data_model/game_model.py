from dataclasses import dataclass, field

from baseball_simulator.data_model.data_model import Batter, Pitcher, Team


@dataclass
class Bases:
    """各塁の走者状態を保持するクラス"""

    first: Batter | None = None
    second: Batter | None = None
    third: Batter | None = None

    def clear(self) -> None:
        """チェンジ時に塁をリセット"""
        self.first = None
        self.second = None
        self.third = None


@dataclass
class StartingLineup:
    team: Team
    starter_pitcher: Pitcher
    lineup: list[Batter]
    positions: dict[Batter, str]


@dataclass
class GameState:
    home_lineup: StartingLineup
    away_lineup: StartingLineup
    home_pitcher_stamina: float = 0.0
    away_pitcher_stamina: float = 0.0

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

    # 現在登板中の投手を保持するフィールド（初期値は先発投手）
    current_home_pitcher: Pitcher = field(init=False)
    current_away_pitcher: Pitcher = field(init=False)

    def __post_init__(self) -> None:
        """初期化時に現在登板中の投手へ先発投手をセット"""
        self.current_home_pitcher = self.home_lineup.starter_pitcher
        self.current_away_pitcher = self.away_lineup.starter_pitcher

    def get_current_batter(self) -> Batter:
        """現在打席に立っている打者（Batter オブジェクト）を取得"""
        if self.is_top:
            return self.away_lineup.lineup[self.away_batter_index]
        return self.home_lineup.lineup[self.home_batter_index]

    def get_current_pitcher(self) -> Pitcher:
        """現在マウンドに立っている守備側の投手（Pitcher オブジェクト）を取得"""
        if self.is_top:
            return self.current_home_pitcher  # 表は Home が守備
        return self.current_away_pitcher  # 裏は Away が守備

    def change_pitcher(self, new_pitcher: Pitcher) -> None:
        """守備側の現在登板中の投手を交代する"""
        if self.is_top:
            self.current_home_pitcher = new_pitcher
        else:
            self.current_away_pitcher = new_pitcher

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

    # プロパティで現在守備側のスタミナを動的に取得・更新できるようにする
    @property
    def current_pitcher_stamina(self) -> float:
        return self.home_pitcher_stamina if self.is_top else self.away_pitcher_stamina

    @current_pitcher_stamina.setter
    def current_pitcher_stamina(self, value: float) -> None:
        if self.is_top:
            self.home_pitcher_stamina = value
        else:
            self.away_pitcher_stamina = value
